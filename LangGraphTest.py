import json

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent

from langchain_community.tools import DuckDuckGoSearchResults
from pydantic import BaseModel

from mao_tools.weather import get_weather



class MaoState(BaseModel):
    nodeA: bool = True
    nodeB: int = 0
    nodeC: int = 0
    nodeD: int = 0


def node1(state):
    print("come in node1")
    state.nodeD = True

def node2(state):
    print("come in node2")
    state.nodeB = 1080
    state.nodeC = "qingdao"


def nodeTrue(state):
    print("come in nodeTrue")
    state.nodeA = False

def nodeFalse(state):
    print("come in nodeFalse")
    state.nodeB += 7181
    state.nodeD = "beijing"

def judge_A(state):
    return state.nodeA

def main():

    builder = StateGraph(MaoState)
    builder.add_node("Node1", node1)
    builder.add_node("NODE2", node2)
    builder.add_node("nodeTrue", nodeTrue)
    builder.add_node("nodeFalse", nodeFalse)

    builder.add_edge(START, "Node1")

    builder.add_conditional_edges("Node1", judge_A, {
        True: "nodeTrue",
        False: "nodeFalse"
    })
    # builder.add_edge("Node1", "nodeTrue")
    # builder.add_edge("nodeTrue", "nodeFalse")

    builder.add_edge("nodeTrue", "NODE2")
    builder.add_edge("NODE2", END)

    builder.add_edge("nodeFalse", END)

    print(builder.edges)
    print(builder.nodes)

    memory = MemorySaver()

    app = builder.compile(checkpointer=memory)
    mmm = app.get_graph(xray=True).draw_mermaid()
    print(mmm)


    thread_config = {"configurable": {"thread_id": "qingdao123"}}
    global_state = MaoState()
    app.invoke(global_state, config=thread_config)


    # "https://blog.csdn.net/m0_37242314/article/details/148592449"

    for chunk in app.stream({"messages": ["你好，我叫bug"]}, thread_config, stream_mode="values"):
        chunk["messages"][-1].pretty_print()


    # app.get_state()
    print(global_state)

    return




    print(f"{get_weather.name} === {get_weather.description} === {get_weather.args}")

    search = DuckDuckGoSearchResults(output_format="list")
    ret = search.invoke("who is Jianwei Mao?")


    tools = [get_weather]






    llm = ChatOpenAI(
        model='Qwen/Qwen3-Coder-480B-A35B-Instruct',
        openai_api_base='https://api-inference.modelscope.cn/v1',
        openai_api_key='ms-7b01568c-9c16-460d-a82c-0d545f209bad',
    )

    llm.bind_tools(tools)

    agent = create_react_agent(model=llm, tools=tools)


    messages = [
        SystemMessage(
            content="You are a helpful assistant."
        ),
        HumanMessage(
            content="上海的天气怎么样，详细介绍一下。"
        ),
    ]
    # data = llm.invoke(messages)
    data = agent.invoke({"messages": messages})
    print(data)



if __name__ == '__main__':
    main()

