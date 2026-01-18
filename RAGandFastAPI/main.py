from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from RAGandFastAPI.ai import AiProcess
from RAGandFastAPI.requestBody import QuerySchema, QueryResponseSchema

load_dotenv()

app = FastAPI()
ai = AiProcess()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/ai", response_model=QueryResponseSchema)
async def ai_response(body: QuerySchema) -> dict:
    query = body.query
    answer = ai.run_ai(query)
    ai.add_context(f"User asked: {query}. AI answered: {answer}")
    return {
        "id": body.id,
        "role": "assistant",
        "content": ai.run_ai(query)
    }
