import streamlit as st
import uuid
from chatbot_back import chatbot, retrieve_threads
from langchain_core.messages import HumanMessage

# this is state {
#     'thread_id': UUID('56f0b4fd-0357-4582-b39f-58a9eea2dc08'),
#     'chat_threads': [
#                       UUID('b3daba92-f104-4962-a9c2-dea2c397354d'),
#                       UUID('56f0b4fd-0357-4582-b39f-58a9eea2dc08')
#                     ],
#     'message_history': [
#                           {'role': 'user', 'content': 'kesse ho bhai'},
#                           {'role': 'assistant', 'content': 'Main theek hoon, shukriya! Aap kaise hain?'}
#                         ]
#     }

                                                    # Utitlity Functions

# generate dynamic thread_id and add it to session
def generate_thread():
    thread_id =  uuid.uuid4()
    return thread_id

# reset old chats
def reset_chat():
    thread_id = generate_thread()
    st.session_state["thread_id"] = thread_id           #Streamlit stateless hai — har user interaction pe poora script re-run hota hai. st.session_state persist karta hai values across reruns.
    add_thread_id(st.session_state["thread_id"])
    st.session_state["message_history"] = []

# load old messages using get_state
def load_conversation(thread_id):
    state = chatbot.get_state(
        config={"configurable": {"thread_id": thread_id}}
    )
    return state.values.get("messages",[])

# store thread id in list so that we remeber it
def add_thread_id(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


                                            # session setup
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []        #message history stores list as value

# [{"role":"user", "content":'Hi'},
#  {"role":"assistant", "content":"hello"}]

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread()    #key with values

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_threads()

add_thread_id(st.session_state["thread_id"])

#########################################################################################################

CONFIG = {'configurable': {'thread_id': st.session_state["thread_id"]}}

                                            # Sidebar UI
st.sidebar.title("Langgraph Chatbot")

if st.sidebar.button("Start New chat"):
    reset_chat()

st.sidebar.header("Conversations")

for thread_id in st.session_state["chat_threads"][::-1]:  #reversed
    if st.sidebar.button(str(thread_id)):
        st.session_state["thread_id"] = thread_id
        messages = load_conversation(thread_id)

        # converting load messages to our format
        temp_messages = []
        for message in messages:
            if isinstance(message, HumanMessage):
                role = "user"
            else:
                role = "assistant"
            temp_messages.append({"role":role, "content":message.content})

        st.session_state["message_history"] = temp_messages   


# Show old messages on ui
for message in st.session_state['message_history']:
    with st.chat_message(message["role"]):
        st.text(message["content"])

# New user query
user_input = st.chat_input("type here")

if user_input:
    st.session_state['message_history'].append({"role":"user", "content":user_input})
    with st.chat_message("user"):
        st.text(user_input)

    #generate answer
    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in  chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config= CONFIG,
                stream_mode = 'messages'
            )
        )
    # append generated message
    st.session_state['message_history'].append({"role":"assistant", "content":ai_message})
    # print("this is state", st.session_state)