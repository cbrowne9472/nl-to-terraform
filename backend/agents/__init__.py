import os
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.callbacks.tracers import LangChainTracer

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

tracer = LangChainTracer(
    project_name=os.getenv("LANGCHAIN_PROJECT", "nl-to-terraform")
)

CODE_FENCE_RE = re.compile(r"^```[a-zA-Z]*\n|\n```$")


def strip_code_fences(code: str) -> str:
    return CODE_FENCE_RE.sub("", code.strip())
