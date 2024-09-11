#package imports
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_chroma import Chroma
import chromadb
from langchain.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint
from langchain.chains import RetrievalQA

#chromadb client
client = chromadb.PersistentClient()

model = "BAAI/bge-base-en"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {"normalize_embeddings": True}
embedding = HuggingFaceBgeEmbeddings(
    model_name=model,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)
    
#collection create
def create_collection(client, collection_name):

    loaders = [PyPDFLoader("C:/Users/PearlSoft LT-119/basic_chatbot/docs/romeo-and-juliet_PDF.pdf")]
    docs = []

    for loader in loaders:
        docs.extend(loader.load())

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(docs)

    for idx, text in enumerate(texts):
        text.metadata["id"] = idx
    
    return client.create_collection(collection_name)
    
    
#model query
def initialize_llm(queries,collection_name):
    # Initialize the HuggingFace model
    llm = HuggingFaceEndpoint(repo_id="mistralai/Mistral-7B-Instruct-v0.2")

    # Define the prompt template
    template = """
    You are an assistant designed to help find answers to the given question based on the provided context. When asked a question,
    provide concise answer to the question in very short paragraphs and not pointwise. Keep the paragraph very brief and answer exactly to the question.
    Only answer question from the document. For questions not from document respond with 'i don't know'. 
    If you do not know the answer, state that you do not know the answer instead of guessing. 

    Context: {context}
    Question: {question}
    Answer: 

    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )

    vectordb = Chroma( 
        embedding_function=embedding, 
        persist_directory="C:/Users/PearlSoft LT-119/basic_chatbot/docs/chroma", 
        client=client, 
        collection_name=collection_name)
    
    retriever = vectordb.as_retriever()
   
    chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, chain_type_kwargs={"prompt": prompt})
    
    result = chain.invoke({"query": queries})

    return result["result"]

    #print(queries,"\n\n",result["result"])


#delete collection
def delete_collection(client, collection_name):
    try:
        client.delete_collection(name=collection_name)
        print(f"Collection '{collection_name}' deleted.")
    except Exception as e:
        print(f"Error deleting collection '{collection_name}': {e}")


def main():

    # main function

    collection_name =  "romeoandjuliet"

    # delete_collection(client, collection_name)

     #create_collection(client, collection_name)
    
    #initialize_llm("Who killed romeo",collection_name)
    
    

if __name__ == "__main__":
    main()
