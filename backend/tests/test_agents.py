import pytest
from backend.agents import llm, tracer
from backend.agents.intent_agent import extract_intent
from backend.agents.resource_agent import plan_resources
from backend.agents.terraform_agent import generate_terraform
from backend.agents.cost_agent import estimate_costs
from backend.config import settings


def test_llm_smoke():
    """Calls GPT-4o with a trivial prompt and confirms a response comes back.
    The call is traced via LangSmith so it should also appear in the
    nl-to-terraform project at smith.langchain.com."""
    response = llm.invoke(
        "Reply with exactly the word: pong",
        config={"callbacks": [tracer], "run_name": "test-agents-smoke"}
    )

    assert response.content is not None
    assert len(response.content) > 0


INTENT_TEST_PROMPTS = [
    "simple web app",
    "highly available web app with auto scaling",
    "web app with postgres database",
    "serverless API",
    "web app with Redis cache and S3 storage",
]


@pytest.mark.parametrize("prompt", INTENT_TEST_PROMPTS)
def test_extract_intent_returns_expected_shape(prompt):
    """Every prompt should come back as a dict matching the Intent schema fields."""
    intent = extract_intent(prompt)

    expected_keys = {
        "region", "availability", "compute_type", "load_balanced",
        "auto_scaling", "min_instances", "max_instances", "database",
        "cache", "storage", "encryption", "estimated_complexity",
    }
    assert expected_keys.issubset(intent.keys())
    assert intent["region"]
    assert intent["compute_type"] in {"ec2", "lambda", "ecs", "eks"}
    assert intent["availability"] in {"single-az", "multi-az"}
    assert intent["estimated_complexity"] in {"simple", "medium", "complex"}


def test_extract_intent_detects_database():
    intent = extract_intent("web app with postgres database")
    assert intent["database"] == "postgres"


def test_extract_intent_detects_cache_and_storage():
    intent = extract_intent("web app with Redis cache and S3 storage")
    assert intent["cache"] == "redis"
    assert intent["storage"] == "s3"


def test_extract_intent_auto_scaling_flag():
    intent = extract_intent("highly available web app with auto scaling")
    assert intent["auto_scaling"] is True
    assert intent["availability"] == "multi-az"


def test_simple_web_app_has_fewer_resources_than_ha():
    simple_intent = extract_intent("simple web server in us-east-1")
    ha_intent = extract_intent("highly available web app with auto scaling")

    simple_resources = plan_resources(simple_intent, settings.max_terraform_resources)
    ha_resources = plan_resources(ha_intent, settings.max_terraform_resources)

    assert len(simple_resources) < len(ha_resources)


def test_multi_az_produces_two_or_more_subnets():
    intent = extract_intent("highly available web app with auto scaling")
    resources = plan_resources(intent, settings.max_terraform_resources)

    subnets = [r for r in resources if r["resource_type"] == "aws_subnet"]
    assert len(subnets) >= 2


def test_database_intent_produces_rds_resource():
    intent = extract_intent("web app with postgres database")
    resources = plan_resources(intent, settings.max_terraform_resources)

    resource_types = {r["resource_type"] for r in resources}
    assert "aws_db_instance" in resource_types


def test_resource_count_never_exceeds_max():
    intent = extract_intent(
        "highly available web app with auto scaling, postgres database, "
        "redis cache, and S3 storage"
    )
    resources = plan_resources(intent, settings.max_terraform_resources)

    assert len(resources) <= settings.max_terraform_resources


def test_generate_terraform_contains_expected_resources():
    intent = extract_intent("highly available web app with auto scaling")
    resources = plan_resources(intent, settings.max_terraform_resources)

    code = generate_terraform(intent, resources, project_name="nl-to-terraform-test")

    assert "terraform {" in code
    assert 'provider "aws"' in code

    for resource in resources:
        assert f'resource "{resource["resource_type"]}"' in code


def test_estimate_costs_returns_expected_shape():
    intent = extract_intent("simple web app")
    resources = plan_resources(intent, settings.max_terraform_resources)

    breakdown = estimate_costs(resources, intent["region"])

    assert "line_items" in breakdown
    assert "total_monthly_usd" in breakdown
    assert "cost_tier" in breakdown
    assert "optimization_tips" in breakdown
    assert breakdown["total_monthly_usd"] >= 0
    assert breakdown["within_budget"] is True


def test_cost_guardrail_flags_over_budget(monkeypatch):
    monkeypatch.setattr(settings, "max_monthly_cost_usd", 0.0)

    # EC2 + ALB-backed resources always carry a non-zero estimated cost,
    # so a $0 budget is guaranteed to be exceeded.
    intent = extract_intent("highly available web app with auto scaling")
    resources = plan_resources(intent, settings.max_terraform_resources)
    breakdown = estimate_costs(resources, intent["region"])

    assert breakdown["total_monthly_usd"] > 0
    assert breakdown["within_budget"] is False
