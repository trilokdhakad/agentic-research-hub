from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
import json
import re

def generate_metadata(chunks, filename):
    # 1. Force Ollama into JSON mode natively
    llm = OllamaLLM(
        model="gemma:2b",
        format="json",
        base_url="http://host.docker.internal:11434"
    )

    content = "\n".join(
        chunk.page_content
        for chunk in chunks[:5]
    )

    # FIX: Double curly braces {{ }} used around the JSON schema 
    # so LangChain knows it's plain text, not a variable.
    prompt = PromptTemplate(
        template="""
You are a document analyst.

Return ONLY valid JSON.

Schema:
{{
    "title": "",
    "summary": "",
    "keywords": []
}}

Rules:
- keywords must be a list
- summary maximum 3 sentences
- no markdown
- no explanations
- output JSON only

Document:
{content}
""",
        input_variables=["content"]
    )

    result = (prompt | llm).invoke({
        "content": content
    })

    print("\n===== METADATA RAW OUTPUT =====")
    print(result)
    print("================================\n")

    # 2. Robust JSON extraction to catch stray markdown
    try:
        cleaned_result = result.strip()
        
        # Strip markdown code blocks if the model ignored the prompt
        if cleaned_result.startswith("```json"):
            cleaned_result = cleaned_result[7:]
        if cleaned_result.startswith("```"):
            cleaned_result = cleaned_result[3:]
        if cleaned_result.endswith("```"):
            cleaned_result = cleaned_result[:-3]
            
        cleaned_result = cleaned_result.strip()
        
        # Isolate the JSON object using regex to ignore preamble text
        match = re.search(r'\{.*\}', cleaned_result, re.DOTALL)
        if match:
            cleaned_result = match.group(0)

        parsed = json.loads(cleaned_result)
        
        return {
            "filename": filename,
            "title": parsed.get("title", "Untitled Document"),
            "summary": parsed.get("summary", "No summary generated."),
            "keywords": parsed.get("keywords", [])
        }
        
    except Exception as e:
        print(f"JSON Parsing Error: {e}")
        return {
            "filename": filename,
            "title": "Extraction Failed",
            "summary": f"Raw output could not be parsed: {result}",
            "keywords": []
        }