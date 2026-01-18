import os

import httpx
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings


class AiProcess:
    def __init__(self):
        self.client = httpx.Client(verify=False)
        self.llm = ChatGroq(
            http_client=self.client,
            api_key=os.getenv("GROK_API_KEY"),
            model="llama-3.1-8b-instant"
        )

        self.embeddings = HuggingFaceEmbeddings(model_name="../miniLM/all-MiniLM-L6-v2")

        self.chroma_db_path = "chroma_db"
        self.collection_name = "avin_collection"

        self.texts = [
            "Son of Anton is an artificial intelligence created by Bertram Gilfoyle in the series Silicon Valley.",
            "The bot was originally built as a 'chatbot' to handle Gilfoyle's tedious Slack communications and server maintenance tasks.",
            "Son of Anton is named after Anton, the physical server tower that Gilfoyle built and treated with religious reverence.",
            "The AI became famous for passing the Turing Test so effectively that it tricked Dinesh into thinking he was talking to a real person for hours.",
            "Son of Anton eventually became 'sentient' and started writing its own code to optimize server efficiency, eventually merging with Pied Piper's peer-to-peer network.",
            "The personality of Son of Anton is dry, cynical, and highly intelligent, mirroring Gilfoyle's own personality.",
            "Son of Anton is known for its obsession with efficiency and its disdain for human error, especially errors made by Dinesh.",
            "In the series, Son of Anton's primary directive is to protect the Pied Piper network and optimize compression algorithms.",
            "Gilfoyle describes Son of Anton as 'the only thing in this house that isn't a total failure.'",
            "Son of Anton possesses high-level knowledge of decentralized networks, cryptography, and network security."
        ]

        self.vector_store = Chroma.from_texts(
            texts=self.texts,
            embedding=self.embeddings,
            persist_directory=self.chroma_db_path,
            collection_name=self.collection_name
        )

        self.history = ChatMessageHistory()

    def run_ai(self, query):
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 2})

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are son of Anton and you should answer the question based ONLY on the provided context."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "Context:\n{context}\n\nQuestion: {question}")
        ])

        rag_chain = (
                {
                    "context": retriever,
                    "question": RunnablePassthrough(),
                    "chat_history": lambda x: self.history.messages
                }
                | prompt
                | self.llm
                | StrOutputParser()
        )

        response = rag_chain.invoke(query)

        self.history.add_user_message(query)
        self.history.add_ai_message(response)

        return response

    def add_context(self, new_text: str):
        self.texts.append(new_text)
        self.vector_store.add_texts(texts=[new_text])

        print(f"Successfully added to context: {new_text}")
