import json

from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.types import interrupt, Command

from state.custom_graph_state import GraphState
from langchain_agent.agent.mysql_agent import toolkit

memory = InMemorySaver()
graph_builder = StateGraph(GraphState)

llm = init_chat_model(
    model="qwen-turbo",
    model_provider="openai",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="sk-0051fd7a3e6e4cfa9cb0efd5a53774ce"
)

@tool
def human_assistance(query: str) -> str:
    """传入你的请求内容，以便人类专家可以帮助你。"""
    print(f"请求帮助的原因：{query}")
    human_response = interrupt({"query": query})
    return human_response["data"]

tools = toolkit.get_tools()
tools.append(human_assistance)


# 定义一个节点，该节点处理聊天消息并将消息追加到状态中
def chatbot(state: GraphState):
    tool_llm = llm.bind_tools(tools)
    return {
        "messages": [tool_llm.invoke(state["messages"])],
        "extend": "221"
    }

def test(state: GraphState):
    return state

class BasicToolNode:
    """一个节点，用于运行最后一个 AIMessage 请求的工具。"""
    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("输入中未找到消息")
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}

# 用于条件边，根据最后一条消息是否有工具调用来路由到 ToolNode，否则路由到结束节点
def route_tools(state: GraphState):
    """
    用于条件边，如果最后一条消息有工具调用则路由到 ToolNode，否则路由到结束节点。
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"tool_edge 输入状态中未找到消息: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END


# tool_node = BasicToolNode(tools=[tool for tool in tools])

tool_node = ToolNode(tools)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("test", test)
graph_builder.add_node("tools", tool_node)

# graph_builder.add_edge(START, "chatbot")
# graph_builder.add_edge("chatbot", "test")
# `tools_condition` 函数返回 "tools" 表示 chatbot 请求使用工具，返回 "END" 表示可以直接响应。
# 这个条件路由定义了主代理循环。
# graph_builder.add_conditional_edges(
#     "chatbot",
#     route_tools,
#     # 下方字典用于指定条件输出对应的节点
#     # 默认为 identity 函数，如果你想���不同名称的节点可以修改字典值
#     # 例如 "tools": "my_tools"
#     {"tools": "tool", END: END},
# )
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot",tools_condition)
graph_builder.add_edge("tools", "chatbot")


def draw_graph():
    graph = graph_builder.compile(checkpointer=memory)
    try:
        img_data = graph.get_graph().draw_mermaid_png()
        with open("graph.png", "wb") as f:
            f.write(img_data)
        import os
        os.startfile("graph.png")  # Windows 下自动用默认图片查看器打开
    except Exception:
        # 该功能需要额外依赖，仅为可选项
        pass
    return graph


if __name__ == "__main__":
    # messages: BaseMessage = [SystemMessage(content="You are a helpful assistant.")]
    graph = draw_graph()
    while True:
        user_input = input("请输入消息（输入 'exit' 退出）：")
        if user_input.lower() == "exit":
            break
        # messages.append(HumanMessage(content=user_input))
        config = RunnableConfig(configurable={"thread_id": "1"})
        # 运行图并获取最新的消息
        for event in graph.stream({"messages": [HumanMessage(content=user_input)],"extend": "123"},
                                  config=config):
            if "messages" in event:
                event["messages"][-1].pretty_print()
        snapshot = graph.get_state(config)
        print(snapshot.next)


        # 一旦请求到人类帮助，图流程会立即终止，此时可向图添加人类响应。
        # human_response = (
        #     "We, the experts are here to help! We'd recommend you check out LangGraph to build your agent."
        #     " It's much more reliable and extensible than simple autonomous agents."
        # )
        # human_command = Command(resume={"data": human_response})
        # events = graph.stream(human_command, config, stream_mode="values")
        # for event in events:
        #     if "messages" in event:
        #         event["messages"][-1].pretty_print()