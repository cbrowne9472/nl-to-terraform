import os
import re
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from . import llm, tracer
from ..terraform.snippets import load_snippet

CODE_FENCE_RE = re.compile(r"^```[a-zA-Z]*\n|\n```$")


def _strip_code_fences(code: str) -> str:
    return CODE_FENCE_RE.sub("", code.strip())

TERRAFORM_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a senior Terraform engineer. Generate production-ready Terraform code.

    Rules:
    - Always start with a terraform block specifying required providers
    - Always include a provider block with the target region
    - Use the snippet templates provided as your foundation
    - Fill in all placeholder values with sensible production defaults
    - Use variables for anything that should be configurable
    - All resources must reference each other correctly (no dangling references)
    - Include tags on every resource: Project, Environment, ManagedBy=terraform
    - Never use deprecated arguments
    - Generate complete, valid HCL only — no markdown, no explanation, just Terraform

    Available snippet templates:
    {snippets}
    """),
    ("human", """Generate Terraform for:
    Intent: {intent}
    Resources needed: {resources}
    Project name: {project_name}
    Region: {region}

    Return complete Terraform HCL only.""")
])


def generate_terraform(intent: dict, resources: list, project_name: str = "myapp") -> str:
    snippets = {r["snippet_key"]: load_snippet(r["snippet_key"]) for r in resources}

    chain = TERRAFORM_PROMPT | llm | StrOutputParser()
    result = chain.invoke(
        {
            "intent": str(intent),
            "resources": str(resources),
            "project_name": project_name,
            "region": intent.get("region", "us-east-1"),
            "snippets": str(snippets)
        },
        config={"callbacks": [tracer], "run_name": "terraform-generation"}
    )
    return _strip_code_fences(result)


def save_terraform(code: str, workspace_dir: str) -> str:
    os.makedirs(workspace_dir, exist_ok=True)
    path = os.path.join(workspace_dir, "main.tf")
    with open(path, "w") as f:
        f.write(code)
    return path
