from langchain_core.messages import SystemMessage, HumanMessage, filter_messages, AIMessage
from langchain_core.runnables import RunnableConfig

from langchain_agent.agent.mysql_agent import agent_executor

if __name__ == "__main__":
    messages = []
    while True:
        user_input = input("请输入查询语句：")
        if user_input.lower() == "exit":
            break
        messages.append(HumanMessage(content=user_input))
        events = agent_executor.stream(
            input={"messages": messages},
            stream_mode="values",
            config=RunnableConfig(recursion_limit=100, max_concurrency=50)
        )
        for index, event in enumerate(events):
            if index != 0:
                messages.append(event["messages"][-1])
            event["messages"][-1].pretty_print()
        # 过滤工具调用的消息
        messages = filter_messages(messages, exclude_tool_calls=True)
    for message in messages:
        print(message)

# print(toolkit.get_context())