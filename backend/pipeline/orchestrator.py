import json
import re
from typing import AsyncGenerator

from ..agents.intent_agent import extract_intent
from ..agents.resource_agent import plan_resources
from ..agents.terraform_agent import generate_terraform
from ..agents.validation_agent import validate_and_fix
from ..agents.cost_agent import estimate_costs
from ..config import settings

SLUG_RE = re.compile(r"[^a-zA-Z0-9]+")


def _workspace_slug(prompt: str) -> str:
    return SLUG_RE.sub("_", prompt[:20]).strip("_").lower() or "run"


def _event(stage: str, status: str, data: dict = None) -> str:
    payload = {"stage": stage, "status": status, **(data or {})}
    return f"data: {json.dumps(payload)}\n\n"


async def run_pipeline(prompt: str) -> AsyncGenerator[str, None]:
    """Streams pipeline progress as Server-Sent Events."""

    workspace_dir = f"{settings.terraform_workspace_dir}/{_workspace_slug(prompt)}"

    yield _event("intent", "running")
    try:
        intent = extract_intent(prompt)
        yield _event("intent", "complete", {"result": intent})
    except Exception as e:
        yield _event("intent", "failed", {"error": str(e)})
        return

    yield _event("resources", "running")
    try:
        resources = plan_resources(intent, settings.max_terraform_resources)
        yield _event("resources", "complete", {"result": resources})
    except Exception as e:
        yield _event("resources", "failed", {"error": str(e)})
        return

    yield _event("terraform", "running")
    try:
        terraform_code = generate_terraform(intent, resources)
        yield _event("terraform", "complete", {"code": terraform_code})
    except Exception as e:
        yield _event("terraform", "failed", {"error": str(e)})
        return

    yield _event("validation", "running")
    try:
        validation = validate_and_fix(terraform_code, workspace_dir)
        if not validation["valid"]:
            yield _event("validation", "failed", {"error": validation["error"]})
            return
        terraform_code = validation["code"]
        yield _event("validation", "complete", {
            "attempts": validation["attempts"],
            "code": terraform_code
        })
    except Exception as e:
        yield _event("validation", "failed", {"error": str(e)})
        return

    yield _event("cost", "running")
    try:
        costs = estimate_costs(resources, intent.get("region", "us-east-1"))

        if costs["total_monthly_usd"] > settings.max_monthly_cost_usd:
            yield _event("cost", "blocked", {
                "reason": (
                    f"Estimated cost ${costs['total_monthly_usd']:.2f}/month "
                    f"exceeds limit of ${settings.max_monthly_cost_usd}"
                ),
                "breakdown": costs
            })
            return

        yield _event("cost", "complete", {"breakdown": costs})
    except Exception as e:
        yield _event("cost", "failed", {"error": str(e)})
        return

    yield _event("ready", "awaiting_approval", {
        "terraform_code": terraform_code,
        "workspace_dir": workspace_dir
    })
