import asyncio
from audio_capture import AsyncAudioCapture, AudioData


async def audio_interrupt_handler(audio_data: AudioData):
    """
    音频打断回调函数
    当检测到音频输入时，此函数会被调用
    """
    print(f"⚠️  音频打断信号触发！检测到音频输入")
    print(f"   数据大小: {len(audio_data.raw_data)} 字节")
    print(f"   时间戳: {audio_data.timestamp}")
    print(f"   采样率: {audio_data.sample_rate} Hz")
    print(f"   声道数: {audio_data.channels}")
    
    # 在这里可以添加主应用的响应逻辑
    # 例如：暂停当前播放的内容、切换到语音识别模式等


async def main():
    """
    示例主函数 - 展示如何在主应用中使用音频捕获组件
    """
    print("=== 异步音频捕获组件使用示例 ===\n")
    
    # 创建音频捕获实例
    audio_capture = AsyncAudioCapture(
        chunk_size=1024,        # 每次读取的音频块大小
        sample_rate=44100,      # 采样率
        channels=1,             # 单声道
        audio_threshold=0.01    # 音频敏感度阈值
    )
    
    # 检查是否有可用的音频设备
    if not await audio_capture.is_device_available():
        print("❌ 错误：未找到可用的音频输入设备")
        return
    
    print("✅ 音频设备可用\n")
    
    # 设置打断回调函数
    # 当检测到音频输入时，会调用此函数
    audio_capture.set_interrupt_callback(audio_interrupt_handler)
    
    try:
        # 启动音频捕获
        print("🚀 启动音频捕获...")
        await audio_capture.start_capture()
        print("✅ 音频捕获已启动\n")
        
        print("👂 正在监听音频输入...")
        print("💡 请尝试说话或制造声音来测试打断功能")
        print("⏰ 测试将持续 20 秒，或按 Ctrl+C 提前退出\n")
        
        # 主循环 - 模拟主应用的运行
        start_time = asyncio.get_event_loop().time()
        test_duration = 20  # 测试持续时间（秒）
        
        while (asyncio.get_event_loop().time() - start_time) < test_duration:
            # 从队列中获取音频数据（非阻塞）
            audio_data = await audio_capture.get_audio_data()
            if audio_data:
                # 处理接收到的音频数据
                print(f"🎵 收到音频数据: {len(audio_data.raw_data)} 字节")
                
                # 这里可以添加音频处理逻辑
                # 例如：传递给语音识别服务、保存到文件等
            
            # 主应用的其他工作
            # 模拟其他任务
            await asyncio.sleep(0.05)  # 50ms，模拟其他处理时间
        
        print(f"\n⏰ 测试时间到 ({test_duration} 秒)，准备停止...")
        
    except KeyboardInterrupt:
        print("\n⏹️  用户中断测试")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
    finally:
        # 清理资源
        print("\n🧹 清理资源...")
        await audio_capture.stop_capture()
        await audio_capture.cleanup()
        print("✅ 测试完成")


# 高级用法示例
async def advanced_example():
    """
    高级用法示例 - 展示更多功能
    """
    print("\n" + "="*50)
    print("=== 高级用法示例 ===\n")
    
    audio_capture = AsyncAudioCapture(
        chunk_size=2048,
        sample_rate=22050,
        channels=1,
        audio_threshold=0.02
    )
    
    if not await audio_capture.is_device_available():
        print("❌ 音频设备不可用")
        return
    
    # 定义自定义打断处理逻辑
    async def custom_interrupt_handler(audio_data: AudioData):
        print(f"🎯 自定义打断处理: 音频长度 {len(audio_data.raw_data)} 字节")
        # 可以在这里执行异步操作
        await asyncio.sleep(0.1)  # 模拟异步处理
        print("   异步处理完成")
    
    audio_capture.set_interrupt_callback(custom_interrupt_handler)
    
    try:
        await audio_capture.start_capture()
        print("🚀 高级测试开始...")
        
        # 使用异步获取方法
        for i in range(10):  # 获取10次音频数据或超时
            audio_data = await audio_capture.get_audio_data_async(timeout=2.0)
            if audio_data:
                print(f"📊 第 {i+1} 次获取到音频数据")
            else:
                print(f"⏳ 第 {i+1} 次未获取到音频数据")
        
    except Exception as e:
        print(f"❌ 高级测试错误: {e}")
    finally:
        await audio_capture.stop_capture()
        await audio_capture.cleanup()


if __name__ == "__main__":
    # 运行基础示例
    asyncio.run(main())
    
    # 运行高级示例
    asyncio.run(advanced_example())