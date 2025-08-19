from langchain.chat_models import init_chat_model
from langchain_community.utilities import SQLDatabase
from langgraph.graph import StateGraph, START, END
from graphstate.custom_message_state import MessageState as message_state, MessageState

graph_builder = StateGraph(message_state)

llm = init_chat_model(
    model="qwen-turbo",
    model_provider="openai",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="sk-0051fd7a3e6e4cfa9cb0efd5a53774ce"
)

# 定义一个节点，该节点处理聊天消息并将消息追加到状态中
def chatbot(state: MessageState):
    return {"messages": [llm.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)


graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()
try:
    img_data = graph.get_graph().draw_mermaid_png()
    with open("graph.png", "wb") as f:
        f.write(img_data)
    import os
    os.startfile("graph.png")  # Windows 下自动用默认图片查看器打开
except Exception:
    # This requires some extra dependencies and is optional
    pass

mysql_database_tool = SQLDatabase.from_uri("mysql+pymysql://root:maomao123123@127.0.0.1:3306/langgraph_test?charset=utf8mb4")