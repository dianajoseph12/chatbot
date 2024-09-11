import random
import time
import chatbot.streamlit as st
from app import initialize_llm, create_embeddingandcollection, delete_collection

st.title("ChatBot")
st.sidebar.header("Sidebar")


options_file_path = "options.txt"

def write_options(options):
    with open(options_file_path, "w") as file:
        for key, value in options.items():
            file.write(f"{key}:{value}\n")



def read_options():
    options = {"Onam" : "onam",
               "Romeo&Juliet" : "romeoandjuliet"}
    try:
        with open(options_file_path, "r") as file:
            for line in file:
                key, value = line.strip().split(":", 1)
                options[key] = value
    except FileNotFoundError:
        pass
    return options
# Load options from file
options = read_options()



with st.sidebar:
    uploaded_file = st.file_uploader('Choose your .pdf file', type="pdf")

    if uploaded_file is not None:
        new_collection = st.text_input("new collection name")
        create_embeddingandcollection(new_collection, uploaded_file)
        
        if new_collection:
            options[new_collection] = new_collection
            write_options(options)


    
# Extract the keys and values from the dictionary
    keys = list(options.keys())
    values = list(options.values())


    selected_key = st.selectbox('Select an option', keys)

# Retrieve the corresponding value for the selected key
# selected_value = options[selected_key]
    collection_name = options[selected_key]


 # Option to delete the selected collection
    if st.button(f"Delete Collection '{collection_name}'"):
        delete_collection(collection_name)
        options.pop(selected_key)
        write_options(options)
        st.success(f"Collection '{collection_name}' deleted.")
       
        st.rerun()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if queries := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(queries)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": queries})

    # Create a placeholder for the "thinking..." message
    thinking_placeholder = st.empty()

    # Display "thinking..." while fetching the answer
    thinking_placeholder.text("thinking...")
    
    result = initialize_llm(queries, collection_name)

    # Clear the "thinking..." message once the result is fetched
    thinking_placeholder.empty()

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(result)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": result})









