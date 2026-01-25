import asyncio
import threading
import queue
import numpy as np
import pyaudio
import time
from typing import Callable, Optional, Any
from dataclasses import dataclass


@dataclass
class AudioData:
    """封装后的音频数据"""
    raw_data: bytes
    sample_rate: int
    channels: int
    frame_count: int
    timestamp: float


class AudioInterruptException(Exception):
    """音频打断异常，用于通知主应用有音频输入"""
    pass


class AsyncAudioCapture:
    """
    异步音频捕获组件

    功能：
    1. 从麦克风读取音频
    2. 将音频封装后返回
    3. 在开始读取到音频时返回一个特殊的打断信号
    """

    def __init__(self,
                 chunk_size: int = 1024,
                 sample_rate: int = 44100,
                 channels: int = 1,
                 audio_threshold: float = 0.01):
        """
        初始化音频捕获器

        Args:
            chunk_size: 每次读取的音频块大小
            sample_rate: 采样率
            channels: 声道数
            audio_threshold: 音频阈值，超过此值认为是有效音频输入
        """
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate
        self.channels = channels
        self.audio_threshold = audio_threshold

        # 音频流相关
        self.audio_interface = pyaudio.PyAudio()
        self.stream = None
        self.is_recording = False

        # 队列用于存储音频数据
        self.audio_queue = queue.Queue(maxsize=100)  # 限制队列大小避免内存溢出

        # 用于控制录音线程
        self.recording_thread = None
        self.stop_event = threading.Event()

        # 打断回调函数
        self.interrupt_callback: Optional[Callable[[AudioData], None]] = None

        # 音频活动状态
        self._audio_active = False
        self._last_audio_activity = 0

        # 用于线程安全的锁
        self._lock = threading.Lock()

    def set_interrupt_callback(self, callback: Callable[[AudioData], None]):
        """
        设置打断回调函数
        
        Args:
            callback: 当检测到音频输入时调用的函数
        """
        self.interrupt_callback = callback

    async def start_capture(self):
        """启动音频捕获"""
        if self.is_recording:
            return

        try:
            # 打开音频流
            self.stream = self.audio_interface.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )

            self.is_recording = True
            self.stop_event.clear()

            # 启动录音线程
            self.recording_thread = threading.Thread(target=self._record_audio)
            self.recording_thread.start()
        except Exception as e:
            print(f"启动音频捕获失败: {e}")
            raise

    async def is_device_available(self) -> bool:
        """检查音频设备是否可用"""
        try:
            device_count = self.audio_interface.get_device_count()
            for i in range(device_count):
                info = self.audio_interface.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:  # 有输入通道的设备
                    return True
            return False
        except Exception:
            return False

    async def stop_capture(self):
        """停止音频捕获"""
        if not self.is_recording:
            return

        self.is_recording = False
        self.stop_event.set()

        if self.recording_thread and self.recording_thread.is_alive():
            try:
                self.recording_thread.join(timeout=2.0)  # 等待最多2秒
            except Exception as e:
                print(f"等待录音线程结束时出错: {e}")

        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception as e:
                print(f"关闭音频流时出错: {e}")
            finally:
                self.stream = None

    def _record_audio(self):
        """在独立线程中录制音频"""
        while self.is_recording and not self.stop_event.is_set():
            try:
                # 读取音频数据
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)

                # 创建音频数据对象
                audio_data = AudioData(
                    raw_data=data,
                    sample_rate=self.sample_rate,
                    channels=self.channels,
                    frame_count=self.chunk_size,
                    timestamp=time.time()
                )

                # 检查是否为有效音频输入
                if self._is_audio_active(data):
                    # 如果之前没有音频活动，则触发打断信号
                    if not self._audio_active:
                        self._audio_active = True
                        # 在主线程中调用打断回调
                        if self.interrupt_callback:
                            # 使用线程安全的方式调度异步回调
                            try:
                                # 尝试获取当前运行的事件循环
                                loop = asyncio.get_running_loop()
                                if loop and not loop.is_closed():
                                    asyncio.run_coroutine_threadsafe(
                                        self._call_interrupt_callback(audio_data),
                                        loop
                                    )
                                else:
                                    # 如果没有运行的循环，尝试创建新的
                                    new_loop = asyncio.new_event_loop()
                                    asyncio.set_event_loop(new_loop)
                                    new_loop.run_until_complete(self._call_interrupt_callback(audio_data))
                                    new_loop.close()
                            except RuntimeError:
                                # 如果无法访问事件循环，创建新的事件循环
                                new_loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(new_loop)
                                new_loop.run_until_complete(self._call_interrupt_callback(audio_data))
                                new_loop.close()
                else:
                    self._audio_active = False

                # 将音频数据放入队列
                try:
                    self.audio_queue.put_nowait(audio_data)
                except queue.Full:
                    # 如果队列满了，丢弃最旧的数据
                    try:
                        self.audio_queue.get_nowait()
                        self.audio_queue.put_nowait(audio_data)
                    except queue.Empty:
                        pass

            except Exception as e:
                print(f"音频录制错误: {e}")
                break

    def _is_audio_active(self, audio_data: bytes) -> bool:
        """
        检测音频是否活跃
        
        Args:
            audio_data: 音频原始数据
            
        Returns:
            是否检测到有效音频输入
        """
        # 将字节数据转换为numpy数组进行分析
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        # 计算音频能量（均方根）
        rms = np.sqrt(np.mean(audio_array.astype(float) ** 2))
        # 如果RMS超过阈值，则认为有音频输入
        return rms > (self.audio_threshold * 32767)  # 32767是16位音频的最大值

    async def _call_interrupt_callback(self, audio_data: AudioData):
        """异步调用打断回调函数"""
        if self.interrupt_callback:
            await self.interrupt_callback(audio_data)

    async def get_audio_data(self) -> Optional[AudioData]:
        """
        获取音频数据

        Returns:
            音频数据对象，如果没有可用数据则返回None
        """
        with self._lock:
            try:
                # 尝试从队列获取音频数据（非阻塞）
                return self.audio_queue.get_nowait()
            except queue.Empty:
                return None

    async def get_audio_data_async(self, timeout: Optional[float] = None) -> Optional[AudioData]:
        """
        异步方式获取音频数据（非阻塞轮询）

        Args:
            timeout: 超时时间（秒），None表示无超时限制

        Returns:
            音频数据对象
        """
        start_time = time.time()
        while True:
            data = await self.get_audio_data()
            if data is not None:
                return data

            # 检查是否超时
            if timeout is not None and (time.time() - start_time) >= timeout:
                return None

            # 短暂休眠以避免过度占用CPU
            await asyncio.sleep(0.001)

    async def get_audio_data_blocking(self, timeout: Optional[float] = None) -> Optional[AudioData]:
        """
        阻塞方式获取音频数据

        Args:
            timeout: 超时时间（秒），None表示无限等待

        Returns:
            音频数据对象
        """
        try:
            if timeout is None:
                with self._lock:
                    return self.audio_queue.get()
            else:
                with self._lock:
                    return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    async def cleanup(self):
        """异步清理资源"""
        try:
            await self.stop_capture()
        except Exception as e:
            print(f"停止捕获时出错: {e}")

        try:
            if hasattr(self, 'audio_interface') and self.audio_interface:
                self.audio_interface.terminate()
        except Exception as e:
            print(f"终止音频接口时出错: {e}")

    def __del__(self):
        """析构函数，确保资源被正确释放"""
        try:
            if hasattr(self, 'audio_interface') and self.audio_interface:
                self.audio_interface.terminate()
        except Exception as e:
            print(f"析构函数中出错: {e}")