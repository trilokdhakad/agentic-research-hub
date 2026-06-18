from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_ollama import OllamaLLM
from database import get_vector_store
from langchain_core.prompts import PromptTemplate
from metadata_store import get_metadata_by_filename  # <-- NEW IMPORT

# 1. State Definition
class GraphState(TypedDict):
    question: str
    plan: str           
    context: List[str]
    generation: str
    sources: List[str]

# 2. PLANNER AGENT
def planner_node(state: GraphState):
    question = state["question"]
    llm = OllamaLLM(model="gemma:2b")
    
    prompt = PromptTemplate(
        template="""You are a senior AI research planner. 
        Break down the user's question into exact search goals and key concepts.
        Do NOT ask the user for information. Do NOT answer the question yet.
        Output ONLY the extraction plan.

        User Question: {question}
        Extraction Plan:""",
        input_variables=["question"]
    )
    
    plan = (prompt | llm).invoke({"question": question})
    
    print(f"\n=== PLANNER AGENT STRATEGY ===\n{plan}\n==============================\n")
    return {"plan": plan.strip()}

# 3. ENRICHED RETRIEVER
def retrieve_node(state: GraphState):
    question = state["question"]
    plan = state.get("plan", "")
    search_query = f"{question} {plan}"

    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    docs = retriever.invoke(search_query)

    # Extract unique sources from the retrieved chunks
    sources = list(set([
        doc.metadata.get("source", "Unknown")
        for doc in docs
    ]))

    print(f"\n===== RETRIEVED {len(docs)} DOCS =====")
    for source in sources:
        print(f"Sourced from: {source}")
    print("========================\n")

    # --- INJECTING METADATA INTELLIGENCE ---
    enriched_context = []
    
    doc_intelligence = []
    for source in sources:
        if source != "Unknown":
            # Fetch the extracted intelligence for this specific document
            meta = get_metadata_by_filename(source)
            if meta:
                meta_info = f"Document Title: {meta.get('title', 'Unknown')}\n"
                meta_info += f"Global Summary: {meta.get('summary', 'None')}\n"
                meta_info += f"Keywords: {', '.join(meta.get('keywords', []))}\n"
                doc_intelligence.append(meta_info)

    if doc_intelligence:
        enriched_context.append("--- GLOBAL DOCUMENT INTELLIGENCE ---")
        enriched_context.extend(doc_intelligence)
        enriched_context.append("\n--- SPECIFIC RETRIEVED EXCERPTS ---")

    # Add the actual raw chunks
    enriched_context.extend([doc.page_content for doc in docs])

    return {
        "context": enriched_context,
        "sources": sources
    }

# 4. WRITER AGENT
def generate_node(state: GraphState):
    question = state["question"]
    context = state["context"]
    plan = state["plan"]
    
    llm = OllamaLLM(model="gemma:2b") 
    
    prompt = PromptTemplate(
        template="""You are an expert research writer.
        First, review this Research Plan: {plan}
        
        Now, execute the plan using ONLY the following Context to answer the Question.
        The Context contains both Global Document Summaries and Specific Excerpts. Use the global summaries to understand the overall context, but ground specific facts in the excerpts.
        
        If the context does not contain the answer, say "I don't have enough information."
        
        Context: 
        {context}
        
        Question: {question}
        Answer:""",
        input_variables=["context", "question", "plan"]
    )
    
    # Context is now a mix of broad summaries and specific chunks
    generation = (prompt | llm).invoke({
        "context": "\n---\n".join(context), 
        "question": question, 
        "plan": plan
    })
    
    return {"generation": generation.strip()}

# 5. Compile the Multi-Agent Flow
workflow = StateGraph(GraphState)

workflow.add_node("planner", planner_node)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("generate", generate_node)

workflow.set_entry_point("planner")
workflow.add_edge("planner", "retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

rag_app = workflow.compile()