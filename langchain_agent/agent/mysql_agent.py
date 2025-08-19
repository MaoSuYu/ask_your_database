from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent

from llms.llm_provider import llm
from prompts.sql_agent_prompts import prompt_template

mysql_database_tool = SQLDatabase.from_uri(
    "mysql+pymysql://root:maomao123123@127.0.0.1:3306/langgraph_test?charset=utf8mb4")
toolkit = SQLDatabaseToolkit(db=mysql_database_tool, llm=llm)
# 打印工具和工具描述
# for tool in toolkit.get_tools():
#     print(tool.name, tool.description)

# print(prompt_template.input_variables)
system_message = prompt_template.format(dialect="mysql", top_k=5)

agent_executor = create_react_agent(llm, toolkit.get_tools(), prompt=SystemMessage(content=system_message.content), )
