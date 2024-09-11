import redis
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_chroma import Chroma
import chromadb
from langchain.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnableMap
import json
# Initialize Redis client
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
client = chromadb.PersistentClient(path="./docs/chroma")


model = "BAAI/bge-base-en"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {"normalize_embeddings": True}
embedding_fn = HuggingFaceBgeEmbeddings(
    model_name=model,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

#collection create
def create_embeddingandcollection(collection_name, uploaded_file):
# def create_embeddingandcollection(collection_name):

    # loaders = [PyPDFLoader("C:/Users/PearlSoft LT-119/basic_chatbot/docs/sample/paris.pdf")]

    if uploaded_file :

        temp_file = "./temp.pdf"
        with open(temp_file, "wb") as file:
            file.write(uploaded_file.getvalue())
            file_name = uploaded_file.name

    loaders = [PyPDFLoader(temp_file)]

    docs = []

    for loader in loaders:
        docs.extend(loader.load())

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(docs)
    embeddings = embedding_fn.embed_documents([text.page_content for text in texts])
    # print(texts)
    # print(embeddings)
   
    try:
        
        collection = client.get_or_create_collection(collection_name)
        for i, (text, embedding) in enumerate(zip(texts, embeddings)):
            ids = f"{collection_name}_{i}"
            # print(f"Generated ID: {ids}")
            collection.upsert(
                ids=[ids],  # ids should be a list
                embeddings=[embedding],  # embeddings should be a list
                metadatas=[{
                    "source": text.metadata['source'],
                    "page": text.metadata['page']
                }],
                documents=[text.page_content]  
            )
        # print("Success")
        
    except Exception as e:
        print("Exception")

#model query
def initialize_llm(query: str, collection_name):
    
    llm = HuggingFaceEndpoint(repo_id="mistralai/Mistral-7B-Instruct-v0.2")
    # llm = HuggingFaceEndpoint(repo_id="mistralai/Mistral-7B-Instruct-v0.3")

    template = """
You are assisting a user based on the following context and conversation history. The user may provide new statements or ask questions. For new statements say "I will remember that".
Use the context and history to respond to question. If certain information (e.g., about a person or entity) is not present in the history, explicitly mention that.

Context: {context}
History: {history}
Current User Input: {question}

If you do not know the answer or the conversation history does not contain the requested information (e.g., about a friend or entity),
 say "The conversation history does not mention any information about [entity_name]."

Answer concisely and avoid guessing. Acknowledge new information when given, and add it to the {history}.
"""



    prompt = PromptTemplate(
        template=template,
        input_variables=["context", "question", "history"]
    )


    context = Chroma( 
        embedding_function=embedding_fn, 
        client=client, 
        collection_name=collection_name,
       )
    
    
    retriever = context.as_retriever(search_kwargs={"k": 4})
    history = r.hgetall('admin3')
    chat_history=json.dumps(history)

    rag_chain = RunnableMap({
        "context": lambda x: retriever.invoke(x["question"]),
        "question": lambda x: x["question"],
       
        "history" : lambda x: chat_history

    }) | prompt | llm | StrOutputParser()

    result = rag_chain.invoke({"question": query,"history":chat_history})
    print("Response : \n" + result)

    r.hset('admin3', mapping={
    query : result
})
    
    # print("history",history)

    return result

#delete collection
def delete_collection(collection_name):
    try:
        client.delete_collection(name=collection_name)
        print(f"Collection '{collection_name}' deleted.")
    except Exception as e:
        print(f"Error deleting collection '{collection_name}': {e}")


def main():

    collection_name =  "diana"

    # delete_collection(collection_name)

    # create_embeddingandcollection(collection_name)
    
    initialize_llm("diana's qualification",collection_name)


if __name__ == "__main__":
    main()




