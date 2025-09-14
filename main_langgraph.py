import time
from datetime import datetime
from typing import TypedDict, Annotated

from IPython.core.display import Image
from IPython.core.display_functions import display
from langchain.chat_models import init_chat_model
from langchain_core.messages import AnyMessage, AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.func import task
from langgraph.graph import StateGraph, add_messages
from langgraph.runtime import Runtime
from langgraph.types import interrupt, Command

from lib.constant import NEED_ID_USER_CHAT_INPUT


class MaoContextSchema(TypedDict):
    llm: ChatOpenAI


class MaoTotalState(TypedDict):

    is_new_session: bool

    messages: Annotated[list[AnyMessage], add_messages]


def session_list_show_and_choose(checkpointer: InMemorySaver):
    return {}

def session_print_and_verify(checkpointer: InMemorySaver):
    return {}

# @task
def llm_inference(llm_server: ChatOpenAI, messages):
    # time.sleep(3)

    response = llm_server.invoke(messages)

    return response.content

def simple_chat(state: MaoTotalState, runtime: Runtime[MaoContextSchema]):

    if state["is_new_session"]:
        user_input = interrupt({"need": NEED_ID_USER_CHAT_INPUT, "cmd_prompt": "请输入问题："})
    else:
        user_input = interrupt({"need": NEED_ID_USER_CHAT_INPUT, "cmd_prompt": "请补充要求："})


    human_msg = HumanMessage(content=user_input)
    state["messages"].append(human_msg)

    ai_content_task = llm_inference(runtime.context["llm"], state["messages"])
    ai_content = ai_content_task.result()

    return {"messages": [human_msg, AIMessage(content=ai_content)], "is_new_session": False}

def main():

    # checkpointer
    checkpointer = InMemorySaver()

    # store



    # LLM
    llm = ChatOpenAI(
        model_name="glm-4.5-flash",  # 私有部署的模型名称
        openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
        openai_api_key="27943078d7714b0a9e63c37a338f1051.GXJ9LixW6DWRTti6"  # 私有服务器的API密钥（如果需要）
    )

    # llm = init_chat_model(model="openai:glm-4.5-flash",
    #                       base_url="https://open.bigmodel.cn/api/paas/v4/",
    #                       api_key="27943078d7714b0a9e63c37a338f1051.GXJ9LixW6DWRTti6",
    #                       disable_streaming=False)


    graph_builder = StateGraph(MaoTotalState, MaoContextSchema)

    # graph_builder.add_node("session_list_show_and_choose", session_list_show_and_choose)
    # graph_builder.add_node("session_print_and_verify", session_print_and_verify)
    # graph_builder.add_node("simple_chat", simple_chat)
    #
    # graph_builder.add_edge(START, "session_list_show_and_choose")
    # graph_builder.add_edge("session_list_show_and_choose", "session_print_and_verify")
    # graph_builder.add_edge("session_print_and_verify", "simple_chat")
    # graph_builder.add_edge("simple_chat", "simple_chat")


    graph_builder.add_node("simple_chat", simple_chat)

    graph_builder.add_edge(START, "simple_chat")
    graph_builder.add_edge("simple_chat", "simple_chat")

    graph = graph_builder.compile(checkpointer=checkpointer)

    mermaid_code = graph.get_graph().draw_mermaid()
    print(mermaid_code)



    config = {"configurable": {"thread_id": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}}
    context = {"llm": llm}

    resume_data = None
    run_data = {"is_new_session": True}
    is_graph_going = True
    while is_graph_going:

        if resume_data is None:
            # start the graph
            # run_data = {TBD}
            pass
        else:
            # resume the graph
            # Attention, start the node at the beginning, not at the interrupt point.
            # run_data = {TBD}
            pass


        for stream_mode, chunk in graph.stream(run_data, stream_mode=["updates", "messages"], config=config, context=context):
            print(stream_mode, chunk)
            if stream_mode == "updates":
                for i in chunk.get("__interrupt__", ()):
                    if i.value["need"] == NEED_ID_USER_CHAT_INPUT:
                        user_word = input(i.value["cmd_prompt"])
                        run_data = Command(resume=user_word)
            elif stream_mode == "messages":
                print(f"*** stream_mode: {stream_mode}, chunk: {chunk}")
            elif stream_mode == "custom":
                print(f"*** stream_mode: {stream_mode}, chunk: {chunk}")
            else:
                print(f"*** stream_mode: {stream_mode}, chunk: {chunk}")



if __name__ == '__main__':
    main()
