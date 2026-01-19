import os

import httpx
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

client = httpx.Client(verify=False)

# made the llm to chat
llm = ChatGroq(
    api_key=os.getenv("GROK_API_KEY"),
    model="llama-3.1-8b-instant",
    http_client=client
)

embeddings = HuggingFaceEmbeddings(model_name="../miniLM/all-MiniLM-L6-v2")

texts = [
    "My name is Avin Madhu",
    "I am a software developer at UST",
    "I am 22 years old",

]

CHROMA_DB_DIR = "chroma_db"
COLLECTION_NAME = "avin_collection"

vectorstore = Chroma.from_texts(
    texts=texts,
    embedding=embeddings,
    persist_directory=CHROMA_DB_DIR,
    collection_name=COLLECTION_NAME
)

retriever = vectorstore.as_retriever()  # a function to call and do a similarity search in the vector DB

template = """Answer the question based only on the following context:
{context}

Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)

rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
)

query = "who is Avin?"
response = rag_chain.invoke(query)

print(response)
