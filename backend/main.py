import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from .agents import llm, tracer
from .agents.intent_agent import extract_intent
from .agents.resource_agent import plan_resources
from .agents.deployment_agent import deploy, destroy
from .config import settings
from .models.schemas import PipelineRequest
from .pipeline.orchestrator import run_pipeline

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


@app.post("/extract-intent")
def extract_intent_endpoint(request: PipelineRequest):
    return extract_intent(request.prompt)


@app.post("/plan-resources")
def plan_resources_endpoint(request: PipelineRequest):
    intent = extract_intent(request.prompt)
    resources = plan_resources(intent, settings.max_terraform_resources)
    return {"intent": intent, "resources": resources}


@app.post("/pipeline/run")
async def run_pipeline_endpoint(request: PipelineRequest):
    return StreamingResponse(
        run_pipeline(request.prompt),
        media_type="text/event-stream"
    )


@app.post("/pipeline/deploy")
async def deploy_endpoint(workspace_dir: str):
    return StreamingResponse(
        deploy(workspace_dir),
        media_type="text/plain"
    )


@app.post("/pipeline/destroy")
async def destroy_endpoint(workspace_dir: str):
    return StreamingResponse(
        destroy(workspace_dir),
        media_type="text/plain"
    )
