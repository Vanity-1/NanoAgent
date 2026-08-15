#!/usr/bin/env python3
"""
快速测试流式工具调用

简化版测试，专注于验证 DeepSeek-V3 的流式工具调用功能
"""

import time

from nanoagent import Agent, OpenAIModel, Runner, function_tool


@function_tool
def get_time() -> str:
    """获取当前时间"""
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@function_tool
def add_numbers(a: int, b: int) -> str:
    """两数相加"""
    return f"{a} + {b} = {a + b}"


def test_streaming_tools():
    """测试流式工具调用"""
    print("🧪 测试 DeepSeek-V3 流式工具调用")
    print("=" * 60)

    # 创建模型和Agent
    model = OpenAIModel(
        model="oneapi-DeepSeek-V3",
        api_key="sk-xxxxxxxxxx",
        base_url="http://xxxx.xxx.xxx.xxx/v1",
        temperature=0.7,
    )

    agent = Agent(
        name="TestAgent",
        instructions="""你是一个助手，必须使用工具来回答问题。

重要规则：
1. 当用户询问时间时，必须调用 get_time 工具
2. 当用户要求计算时，必须调用 add_numbers 工具
3. 不要直接回答，一定要使用工具获取准确信息
4. 请用中文回答

可用工具：
- get_time(): 获取当前时间
- add_numbers(a, b): 计算两个数字的和""",
        model=model,
        tools=[get_time, add_numbers],
    )

    # 测试用例
    test_cases = [
        "现在几点了？",
        "帮我计算 25 + 17",
        "先告诉我现在时间，然后计算 100 + 200",
    ]

    for i, question in enumerate(test_cases, 1):
        print(f"\n📝 测试 {i}: {question}")
        print("-" * 60)

        start_time = time.time()
        first_chunk_time = None

        for event in Runner.run_stream(agent, question):
            current_time = time.time()

            if event.type.value == "answer_delta":
                if first_chunk_time is None:
                    first_chunk_time = current_time
                    print(f"⚡ TTFB: {first_chunk_time - start_time:.3f}秒")
                    print("🤖 回答: ", end="")
                print(event.content, end="", flush=True)

            elif event.type.value == "thinking_delta":
                if first_chunk_time is None:
                    first_chunk_time = current_time
                    print(f"⚡ TTFB: {first_chunk_time - start_time:.3f}秒")
                    print("💭 思考: ", end="")
                print(event.content, end="", flush=True)

            elif event.type.value == "tool_call":
                print(f"\n🔧 调用工具: {event.tool_name}({event.tool_args})")

            elif event.type.value == "tool_result":
                print(f"📊 工具结果: {event.tool_result}")

            elif event.type.value == "answer":
                total_time = time.time() - start_time
                print(f"\n✅ 完成! 总时间: {total_time:.3f}秒")

        print("\n" + "=" * 60)


if __name__ == "__main__":
    test_streaming_tools()
