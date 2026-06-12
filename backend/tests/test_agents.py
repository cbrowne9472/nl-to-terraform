from backend.agents import llm, tracer


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
