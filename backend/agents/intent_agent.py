from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import Literal
from . import llm, tracer

# "none" is used instead of null for database/cache/storage because OpenAI
# function-calling reliably omits or nulls out optional/nullable fields;
# a flat required enum is filled in consistently and translated back to
# None below to match the public Optional[str] contract.
NONE = "none"


class Intent(BaseModel):
    region: str
    availability: Literal["single-az", "multi-az"]
    compute_type: Literal["ec2", "lambda", "ecs", "eks"]
    load_balanced: bool
    auto_scaling: bool
    min_instances: int
    max_instances: int
    database: Literal["postgres", "mysql", "dynamodb", NONE]
    cache: Literal["redis", "memcached", NONE]
    storage: Literal["s3", NONE]
    encryption: bool
    estimated_complexity: Literal["simple", "medium", "complex"]


INTENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an AWS solutions architect. Extract infrastructure requirements
    from natural language descriptions into the given schema.
    If something is not mentioned, use sensible production defaults.
    For region, default to us-east-1 if not specified.
    For availability, default to multi-az for production workloads.
    compute_type must describe the compute platform (ec2, lambda, ecs, or eks),
    never a specific instance size or type.
    Set database/cache/storage to "none" when the description does not call for them,
    and to the matching enum value when it does (e.g. "postgres" for a Postgres database,
    "redis" for a Redis cache, "s3" for object storage)."""),
    ("human", "Extract infrastructure intent from: {prompt}")
])


def extract_intent(prompt: str) -> dict:
    chain = INTENT_PROMPT | llm.with_structured_output(Intent)
    result = chain.invoke(
        {"prompt": prompt},
        config={"callbacks": [tracer], "run_name": "intent-extraction"}
    )
    data = result.model_dump() if isinstance(result, Intent) else Intent.model_validate(result).model_dump()
    for key in ("database", "cache", "storage"):
        if data[key] == NONE:
            data[key] = None
    return data
