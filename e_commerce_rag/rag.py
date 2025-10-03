import json
import uuid
from time import time
from openai import OpenAI
from qdrant_client import QdrantClient, models
from fastembed import TextEmbedding

from . import ingest

client_openai = OpenAI()
qdrant_client = QdrantClient("http://qdrant:6333")
model_handle = "jinaai/jina-embeddings-v2-small-en"
collection_name = "project-sparse-and-dense"

def rrf_search(query: str, limit: int = 4) -> list[dict]:
    try:
        result_points = qdrant_client.query_points(
            collection_name="project-sparse-and-dense",
            prefetch=[
                models.Prefetch(
                    query=models.Document(
                        text=query,
                        model="jinaai/jina-embeddings-v2-small-en",
                    ),
                    using="jina-small",
                    limit=(3 * limit),
                ),
                models.Prefetch(
                    query=models.Document(
                        text=query,
                        model="Qdrant/bm25",
                    ),
                    using="bm25",
                    limit=(3 * limit),
                ),
            ],
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            with_payload=True,
        )

        return [point.payload for point in result_points.points]

    except Exception as e:
        print(f"[WARN] Hybrid search failed: {e}. Falling back to dense search...")

        # ✅ fallback: only dense search
        result_points = qdrant_client.query_points(
            collection_name="project-sparse-and-dense",
            query=models.Document(
                text=query,
                model="jinaai/jina-embeddings-v2-small-en",
            ),
            using="jina-small",
            limit=limit,
            with_payload=True,
        )

        return [point.payload for point in result_points.points]

def build_prompt(query, search_results):
    prompt_template = """
            You're are the customer service chatbot of an e-commerce platform. Answer the QUESTION based on the CONTEXT from the FAQ database.
            Use only the facts from the CONTEXT when answering the QUESTION.
            
            QUESTION: {question}
            
            CONTEXT: 
            {context}
            """.strip()

    context = ""
    
    for doc in search_results:
        context = context + f"prompt: {doc['prompt']}\nresponse: {doc['response']}\n\n"
    
    prompt = prompt_template.format(question=query, context=context).strip()
    return prompt

def llm(prompt, model="gpt-4o-mini"):
    response = client_openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    
    answer = response.choices[0].message.content

    token_stats = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
    }
    
    return answer, token_stats

evaluation_prompt_template = """
You are an expert evaluator for a RAG system.
Your task is to analyze the relevance of the generated answer to the given question.
Based on the relevance of the generated answer, you will classify it
as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

Here is the data for evaluation:

Question: {question}
Generated Answer: {answer}

Please analyze the content and context of the generated answer in relation to the question
and provide your evaluation in parsable JSON without using code blocks:

{{
  "Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
  "Explanation": "[Provide a brief explanation for your evaluation]"
}}
""".strip()

def evaluate_relevance(question, answer):
    prompt = evaluation_prompt_template.format(question=question, answer=answer)
    evaluation, tokens = llm(prompt, model="gpt-4o-mini")

    try:
        json_eval = json.loads(evaluation)
        return json_eval, tokens
    except json.JSONDecodeError:
        result = {"Relevance": "UNKNOWN", "Explanation": "Failed to parse evaluation"}
        return result, tokens
    
def calculate_openai_cost(model, tokens):
    openai_cost = 0

    if model == "gpt-4o-mini":
        openai_cost = (
            tokens["prompt_tokens"] * 0.00015 + tokens["completion_tokens"] * 0.0006
        ) / 1000
    else:
        print("Model not recognized. OpenAI cost calculation failed.")

    return openai_cost


def rag(query, model="gpt-4o-mini"):
     
    conversation_id = str(uuid.uuid4())
    t0 = time()

    search_results = rrf_search(query)
    prompt = build_prompt(query, search_results)
    answer, token_stats = llm(prompt)
    relevance, rel_token_stats = evaluate_relevance(query, answer)

    t1 = time()
    took = t1 - t0

    openai_cost_rag = calculate_openai_cost(model, token_stats)
    openai_cost_eval = calculate_openai_cost(model, rel_token_stats)

    openai_cost = openai_cost_rag + openai_cost_eval

    answer_data = {
         "conversation_id": conversation_id,
         "answer": answer,
         "token_stats": token_stats,
         "model_used": model,
         "response_time": took,
         "relevance": relevance.get("Relevance", "UNKNOWN"),
         "relevance_explanation": relevance.get(
              "Explanation", "Failed to parse evaluation"
          ),
         "prompt_tokens": token_stats["prompt_tokens"],
         "completion_tokens": token_stats["completion_tokens"],
         "total_tokens": token_stats["total_tokens"],
         "eval_prompt_tokens": rel_token_stats["prompt_tokens"],
         "eval_completion_tokens": rel_token_stats["completion_tokens"],
         "eval_total_tokens": rel_token_stats["total_tokens"],
         "openai_cost": openai_cost,
     }

    return answer_data