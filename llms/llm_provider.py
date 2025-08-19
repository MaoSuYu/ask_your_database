from langchain.chat_models import init_chat_model

llm = init_chat_model(
    model="qwen-turbo",
    model_provider="openai",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="sk-0051fd7a3e6e4cfa9cb0efd5a53774ce",
    streaming=True,
)
