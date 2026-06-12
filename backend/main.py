import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .agents import llm, tracer

app = FastAPI(title="NL to Terraform", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/")
def root():
    return {"message": "NL to Terraform API"}


@app.get("/test-llm")
def test_llm():
    response = llm.invoke(
        "Reply with a short confirmation that the LangChain to GPT-4o connection is working.",
        config={"callbacks": [tracer], "run_name": "test-llm-endpoint"}
    )
    return {"response": response.content}
