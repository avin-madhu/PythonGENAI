import os

import httpx
from dotenv import load_dotenv
from llama_index.core import (
    Settings,
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage
)
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.postprocessor import MetadataReplacementPostProcessor
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq

load_dotenv()
PERSIST_DIR = "./storage"
DATA_FILE = "data/avin.txt"

api_key = os.getenv("GROQ_API_KEY")

client = httpx.Client(verify=False)

Settings.llm = Groq(
    model="llama-3.3-70b-versatile",
    api_key=api_key,
    http_client=client
)

Settings.embed_model = HuggingFaceEmbedding(model_name="../miniLM/all-MiniLM-L6-v2")


def get_or_build_index():
    if not os.path.exists(PERSIST_DIR):
        print("Creating new index...")
        node_parser = SentenceWindowNodeParser.from_defaults(
            window_size=3,
            window_metadata_key="window",
            original_text_metadata_key="original_text",
        )
        documents = SimpleDirectoryReader(input_files=[DATA_FILE]).load_data()
        index = VectorStoreIndex.from_documents(documents, transformations=[node_parser])
        index.storage_context.persist(persist_dir=PERSIST_DIR)
    else:
        print("Loading index from disk...")
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)
    return index


index = get_or_build_index()


def query_knowledge_base(query_str):
    postprocessor = MetadataReplacementPostProcessor(target_metadata_key="window")

    query_engine = index.as_query_engine(
        similarity_top_k=3,
        node_postprocessors=[postprocessor]
    )

    response = query_engine.query(query_str)
    return response


if __name__ == "__main__":
    query = "who is Avin?"
    print(f"\nQUERY: {query}")
    print("-" * 30)

    try:
        result = query_knowledge_base(query)
        print(f"RESULT: {result}")
    except Exception as e:
        print(f"ERROR: {e}")
