import streamlit as st

#st.session_state  #ye every new enter pe erase nhi hoti h 

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []


#loading message
for message in st.session_state['message_history']:
    with st.chat_message(message["role"]):
        st.text(message["content"])

# {
#     "role": "user",
#     "message":"hi"
# }

user_input = st.chat_input("type here")

if user_input:
    st.session_state['message_history'].append({"role":"user", "content":user_input})
    with st.chat_message("user"):
        st.text(user_input)

    st.session_state['message_history'].append({"role":"assistant", "content":user_input})
    with st.chat_message("assistant"):
        st.text(user_input)

print(st.session_state['message_history'])