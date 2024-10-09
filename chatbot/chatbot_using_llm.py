import re
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
from demo.settings import BASE_DIR
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain

#initialize llm
llm = HuggingFaceEndpoint(repo_id="mistralai/Mistral-7B-Instruct-v0.3")

#initialize redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

#initialize chroma
client = chromadb.PersistentClient(path="./chroma")

#initialize embedding
model = "BAAI/bge-base-en"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {"normalize_embeddings": True}
embedding_fn = HuggingFaceBgeEmbeddings(
    model_name=model,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

#creating embedding and collection
def create_embeddingandcollection(collection_name, file_name):
        #uploading a doc
        doc_file_path=BASE_DIR / "media" / "document" / file_name.name

        loaders = [PyPDFLoader(doc_file_path)]
        
        docs = []

        for loader in loaders:
            docs.extend(loader.load())
        #splitting the doc
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        texts = text_splitter.split_documents(docs)
        embeddings = embedding_fn.embed_documents([text.page_content for text in texts])
        #creating and upserting collection
        try:
            collection = client.get_or_create_collection(collection_name)
            for i, (text, embedding) in enumerate(zip(texts, embeddings)):
                ids = f"{collection_name}_{i}"
                collection.upsert(
                    ids=[ids],  
                    embeddings=[embedding],  
                    metadatas=[{
                        "source": text.metadata['source'],
                        "page": text.metadata['page']
                    }],
                    documents=[text.page_content]  
                )
            return True
        
        except Exception as e:
            
            return False

#retrieving from chroma
def initialize_llm(redis_key, userMessage, selected_collection):
    db = SQLDatabase.from_uri("sqlite:///D:/django/chatbot_demo/demo/db.sqlite3")
    db_chain = create_sql_query_chain(llm, db)

    if selected_collection == "system":
        response = db_chain.invoke({"question": userMessage})
        final_result = db.run(response)
        return final_result

      
    else:

        template = """Answer the question based only on the following context:
        {context} . If an out of context question is asked, reply with i don't know, instead of guessing
    
        Question: {question}
        """
    
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        context = Chroma( 
            embedding_function=embedding_fn, 
            client=client, 
            collection_name=selected_collection
        )
        
        retriever = context.as_retriever(search_kwargs={"k": 1})
        
        history = r.hgetall(redis_key)
        
        chat_history=json.dumps(history)
        
        rag_chain = RunnableMap({
        "context": lambda x: retriever.invoke(x["question"]),
        "question": lambda x: x["question"],

    }) | prompt | llm | StrOutputParser()

        retrieved_context = retriever.invoke(userMessage)
        
        result = rag_chain.invoke({"question": userMessage})
    
        final_result = re.sub(r'-+', '', result).strip()
        
        r.hset(redis_key, mapping={
        userMessage : final_result
    })
        return final_result
      

#delete collection
def delete_collection(collection_name):
    try:
        client.delete_collection(name=collection_name)
        print(f"Collection '{collection_name}' deleted.")
    except Exception as e:
        print(f"Error deleting collection '{collection_name}': {e}")






