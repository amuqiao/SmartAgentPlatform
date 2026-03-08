# -*- coding: utf-8 -*-
"""Test script to verify Qwen model configuration"""
import asyncio
import os
from agentscope.model import DashScopeChatModel
from agentscope.message import TextBlock

async def test_qwen_model():
    # 创建 Qwen 模型实例
    model = DashScopeChatModel(
        model_name="qwen-plus",
        api_key=os.getenv("DASHSCOPE_API_KEY")
    )

    # 测试模型生成
    print("Testing Qwen model...")
    # 创建消息列表，使用正确的格式
    messages = [{"role": "user", "content": "你好，Qwen！请介绍一下你自己。"}]
    # 异步调用模型
    response = await model(messages)
    print("Response:")
    # 检查返回值类型
    if hasattr(response, '__aiter__'):
        # 处理异步生成器
        async for chunk in response:
            if isinstance(chunk, dict):
                # 处理字典类型的返回值
                if 'text' in chunk:
                    print(chunk['text'])
                elif 'content' in chunk:
                    print(chunk['content'])
                else:
                    print(chunk)
            elif hasattr(chunk, 'text'):
                print(chunk.text)
            else:
                print(chunk)
    elif isinstance(response, dict):
        # 处理字典类型的返回值
        if 'text' in response:
            print(response['text'])
        elif 'content' in response:
            print(response['content'])
        else:
            print(response)
    elif hasattr(response, 'text'):
        print(response.text)
    else:
        print(response)
    print("\nTest completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_qwen_model())
