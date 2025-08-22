from langchain_core.messages import SystemMessage, HumanMessage, filter_messages, AIMessage, BaseMessage
from langchain_core.runnables import RunnableConfig

from langchain_agent.agent.mysql_agent import *
from llms.llm_provider import llm
from prompts.sql_agent_prompts import needs_analyse_prompt_template

if __name__ == "__main__":
    messages: BaseMessage = []
    print(
        """
            请选择模式：
            1. 需求分析与SQL分解助手
            2. SQL Agent
        """
    )
    user_input = input("请选择：")
    if user_input.lower() == "exit":
        exit(0)
    elif user_input.lower() == "1":
        messages.append(needs_analyse_prompt_template.format(dialect="mysql", top_k=5))
        while True:
            user_input = input("请输入查询语句：")
            if user_input.lower() == "exit":
                exit()
            messages.append(needs_analyse_prompt_template.format(dialect="mysql", top_k=5))
            messages.append(HumanMessage(content=user_input))
            events = llm.stream(messages)
            for index, event in enumerate(events):
                print(event.content, end="", flush=True)

    elif user_input.lower() == "2":
        pass
        # events = sql_execute_agent.stream(
        #     input={"messages": messages},
        #     stream_mode="values",
        #     config=RunnableConfig(recursion_limit=100, max_concurrency=50)
        # )
        # for index, event in enumerate(events):
        #     if index != 0:
        #         messages.append(event["messages"][-1])
        #     event["messages"][-1].pretty_print()
        # # 过滤工具调用的消息
        # messages = filter_messages(messages, exclude_tool_calls=True)
    for message in messages:
        print(message)

# print(toolkit.get_context())
