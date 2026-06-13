from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from . import llm, tracer
from ..config import settings
from ..pricing.aws_pricing import estimate_monthly_cost

COST_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an AWS cost analyst. Given a list of resources and their pricing data,
    produce a clean itemized cost breakdown.

    Return JSON with:
    - line_items: array of {{resource, monthly_cost_usd, notes}}
    - total_monthly_usd: sum of all line items
    - cost_tier: "low" (<$50) | "medium" ($50-$200) | "high" (>$200)
    - optimization_tips: array of 2-3 cost saving suggestions
    """),
    ("human", "Produce cost breakdown for resources: {resources}\nPricing data: {pricing_data}")
])


def estimate_costs(resources: list, region: str = "us-east-1") -> dict:
    pricing_data = []
    for resource in resources:
        cost = estimate_monthly_cost(
            resource["resource_type"],
            {"region": region, "instance_count": 2}
        )
        pricing_data.append({
            "resource_type": resource["resource_type"],
            "name": resource["name"],
            "estimated_monthly_usd": cost
        })

    chain = COST_PROMPT | llm | JsonOutputParser()
    result = chain.invoke(
        {"resources": str(resources), "pricing_data": str(pricing_data)},
        config={"callbacks": [tracer], "run_name": "cost-estimation"}
    )
    result["within_budget"] = result["total_monthly_usd"] <= settings.max_monthly_cost_usd
    return result
