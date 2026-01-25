import asyncio
import time
from audio_capture import AsyncAudioCapture, AudioData


async def interrupt_handler(audio_data: AudioData):
    """打断回调函数"""
    print(f"检测到音频输入！时间戳: {audio_data.timestamp}, 大小: {len(audio_data.raw_data)} 字节")
    # 可以在这里添加主应用的响应逻辑


async def main():
    """测试主函数"""
    print("初始化音频捕获器...")
    
    # 创建音频捕获实例
    audio_capture = AsyncAudioCapture(
        chunk_size=1024,
        sample_rate=44100,
        channels=1,
        audio_threshold=0.01  # 可根据实际情况调整阈值
    )
    
    # 检查设备是否可用
    if not await audio_capture.is_device_available():
        print("错误：未找到可用的音频输入设备")
        return
    
    print("音频设备可用")
    
    # 设置打断回调
    audio_capture.set_interrupt_callback(interrupt_handler)
    
    try:
        print("启动音频捕获...")
        await audio_capture.start_capture()
        
        print("开始监听音频输入，按 Ctrl+C 停止...")
        
        # 运行一段时间进行测试
        start_time = time.time()
        duration = 10  # 测试持续时间（秒）
        
        while time.time() - start_time < duration:
            # 获取音频数据
            audio_data = await audio_capture.get_audio_data()
            if audio_data:
                print(f"收到音频数据: {len(audio_data.raw_data)} 字节, 时间戳: {audio_data.timestamp}")
            
            # 短暂休眠以避免过度占用CPU
            await asyncio.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        print("停止音频捕获...")
        await audio_capture.stop_capture()
        print("清理资源...")
        await audio_capture.cleanup()
        print("测试完成")


if __name__ == "__main__":
    asyncio.run(main())