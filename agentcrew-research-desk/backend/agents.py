"""
Agent crew definitions for AgentCrew Research Desk.

Three agents collaborate on a research topic:
  1. Researcher - gathers facts using a web search tool
  2. Writer     - synthesizes findings into a clear report
  3. Critic     - reviews the report for gaps, bias, and clarity

All agents run on a local Ollama model, so no external LLM API key is required.
Swap OLLAMA_MODEL in .env to any model you've pulled (llama3.1, mistral, qwen2.5, etc).
"""
import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
from langchain_community.llms import Ollama
from duckduckgo_search import DDGS

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")

llm = Ollama(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL, temperature=0.3)


@tool("Web Search")
def web_search(query: str) -> str:
    """Search the web for a query and return the top results as text."""
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=6))
    if not results:
        return "No results found."
    return "\n\n".join(
        f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}"
        for r in results
    )


def build_crew(topic: str) -> Crew:
    researcher = Agent(
        role="Senior Research Analyst",
        goal=f"Gather accurate, well-sourced facts about: {topic}",
        backstory=(
            "You are a meticulous analyst who never states a claim without a source. "
            "You prioritize recent, authoritative information and flag uncertainty."
        ),
        tools=[web_search],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    writer = Agent(
        role="Technical Writer",
        goal="Turn raw research into a clear, well-structured report",
        backstory=(
            "You write for a smart but time-pressed reader. You organize findings "
            "into sections with headers, avoid fluff, and keep claims traceable to sources."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    critic = Agent(
        role="Editorial Critic",
        goal="Identify gaps, bias, or unclear reasoning in the draft report",
        backstory=(
            "You are a skeptical editor. You check whether claims are supported, "
            "whether counterpoints are missing, and whether the structure serves the reader."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    research_task = Task(
        description=f"Research the topic '{topic}'. Collect key facts, figures, and sources.",
        expected_output="A bulleted list of findings, each with a source URL.",
        agent=researcher,
    )

    write_task = Task(
        description="Using the research findings, write a structured report with an "
        "introduction, 2-4 themed sections, and a conclusion.",
        expected_output="A markdown report with headers.",
        agent=writer,
        context=[research_task],
    )

    critique_task = Task(
        description="Review the draft report. List concrete issues (missing evidence, "
        "one-sided framing, unclear sections) and suggest fixes. If the report is solid, say so briefly.",
        expected_output="A short critique with actionable notes.",
        agent=critic,
        context=[write_task],
    )

    return Crew(
        agents=[researcher, writer, critic],
        tasks=[research_task, write_task, critique_task],
        process=Process.sequential,
        verbose=True,
    )
