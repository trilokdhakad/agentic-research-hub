from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_ollama import OllamaLLM
from database import get_vector_store
from langchain_core.prompts import PromptTemplate
from metadata_store import get_metadata_by_filename


class GraphState(TypedDict):
    question: str
    plan: str
    context: List[str]
    generation: str
    sources: List[str]


# ==================================================
# PLANNER AGENT
# ==================================================

def planner_node(state: GraphState):
    question = state["question"]

    llm = OllamaLLM(model="gemma:2b")

    prompt = PromptTemplate(
        template="""
You are a retrieval planning agent.

Generate a concise retrieval plan for answering the question.

Rules:
- Output at most 3 retrieval goals.
- Each goal must be one short sentence.
- Focus on what information should be found.
- Do NOT answer the question.
- Do NOT explain your reasoning.
- Do NOT ask for clarification.

Question:
{question}

Retrieval Plan:
""",
        input_variables=["question"]
    )

    plan = (prompt | llm).invoke({
        "question": question
    })

    print(
        f"\n=== PLANNER AGENT STRATEGY ===\n"
        f"{plan}\n"
        f"==============================\n"
    )

    return {
        "plan": plan.strip()
    }

# ==================================================
# RETRIEVER
# ==================================================

def retrieve_node(state: GraphState):
    question = state["question"]

    vector_store = get_vector_store()

    retriever = vector_store.as_retriever(
        search_kwargs={"k": 10}
    )

    docs = retriever.invoke(question)

    print("\n===== RETRIEVED DOCS =====")
    print(f"QUESTION: {question}")

    for i, doc in enumerate(docs):
        print(f"\n----- CHUNK {i+1} -----")
        print(doc.page_content[:500])

    print("\n========================\n")

    sources = list(
        set(
            doc.metadata.get("source", "Unknown")
            for doc in docs
        )
    )

    enriched_context = []

    metadata_sections = []

    for source in sources:

        if source == "Unknown":
            continue

        meta = get_metadata_by_filename(source)

        if meta:

            metadata_text = f"""
DOCUMENT TITLE:
{meta.get("title", "")}

DOCUMENT SUMMARY:
{meta.get("summary", "")}
"""

            metadata_sections.append(
                metadata_text.strip()
            )

    # First add retrieved chunks
    enriched_context.extend(
        doc.page_content
        for doc in docs
    )

    # Then add metadata
    if metadata_sections:

        enriched_context.append(
            "\n=== DOCUMENT INTELLIGENCE ==="
        )

        enriched_context.extend(
            metadata_sections
        )

    return {
        "context": enriched_context,
        "sources": sources
    }


# ==================================================
# WRITER AGENT
# ==================================================

def generate_node(state: GraphState):
    question = state["question"]
    context = state["context"]
    plan = state["plan"]

    llm = OllamaLLM(model="gemma:2b")

    prompt = PromptTemplate(
        template="""
You are an expert research assistant.

First review the research plan:

{plan}

You have access to:

1. Document Intelligence
   - title
   - summary

2. Retrieved document excerpts


Rules:

- Retrieved document excerpts are the primary source of truth.
- Use document summaries only for high-level understanding.
- When answering factual questions, prioritize information found in retrieved excerpts.
- Do not ignore explicit facts present in the excerpts.
- Do not invent information.
- If the answer cannot be found in the provided context, say:

"I don't have enough information in the uploaded documents."

Context:

{context}

Question:

{question}

Answer:
""",
        input_variables=[
            "context",
            "question",
            "plan"
        ]
    )

    generation = (prompt | llm).invoke({
        "context": "\n\n".join(context),
        "question": question,
        "plan": plan
    })

    return {
        "generation": generation.strip()
    }


# ==================================================
# GRAPH
# ==================================================

workflow = StateGraph(GraphState)

workflow.add_node(
    "planner",
    planner_node
)

workflow.add_node(
    "retrieve",
    retrieve_node
)

workflow.add_node(
    "generate",
    generate_node
)

workflow.set_entry_point(
    "planner"
)

workflow.add_edge(
    "planner",
    "retrieve"
)

workflow.add_edge(
    "retrieve",
    "generate"
)

workflow.add_edge(
    "generate",
    END
)

rag_app = workflow.compile()