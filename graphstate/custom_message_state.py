from typing import Annotated

from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class MessageState(TypedDict):
    # 消息的类型为 "list"。注解中的 `add_messages` 函数定义了如何更新此状态键
    # （在此情况下，它将消息追加到列表中，而不是覆盖它们）
    messages: Annotated[list, add_messages]


