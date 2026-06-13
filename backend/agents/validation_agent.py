from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from . import llm, tracer, strip_code_fences
from .terraform_agent import save_terraform
from ..tools.terraform_tools import run_terraform_init, run_terraform_validate

FIX_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Terraform expert. Fix the Terraform code based on the validation error.
    Return only the corrected complete Terraform HCL. No explanation. No markdown. Just code."""),
    ("human", """Terraform code that failed validation:
{code}

Validation error:
{error}

Return the corrected Terraform code only.""")
])


def validate_and_fix(terraform_code: str, workspace_dir: str, max_attempts: int = 3) -> dict:
    current_code = terraform_code

    for attempt in range(1, max_attempts + 1):
        save_terraform(current_code, workspace_dir)

        init_result = run_terraform_init(workspace_dir)
        if not init_result["success"]:
            return {"valid": False, "code": current_code,
                    "error": init_result["error"], "attempts": attempt}

        validate_result = run_terraform_validate(workspace_dir)

        if validate_result["success"]:
            return {"valid": True, "code": current_code,
                    "error": None, "attempts": attempt}

        if attempt < max_attempts:
            chain = FIX_PROMPT | llm | StrOutputParser()
            current_code = strip_code_fences(chain.invoke(
                {"code": current_code, "error": validate_result["error"]},
                config={"callbacks": [tracer], "run_name": f"validation-fix-attempt-{attempt}"}
            ))

    return {"valid": False, "code": current_code,
            "error": validate_result["error"], "attempts": max_attempts}
