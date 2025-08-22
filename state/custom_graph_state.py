from operator import add
from typing import Annotated

from langgraph.graph import MessagesState

class GraphState(MessagesState):
    extend: Annotated[str, add]

