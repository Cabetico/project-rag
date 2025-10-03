# e-commerce-rag/app.py
import uuid
from flask import Flask, request, jsonify
import traceback
from .rag import rag
from . import db

app = Flask(__name__)

# # ✅ Initialize collection only once before workers start
# with app.app_context():
#     ingest.load_index()

@app.route("/question", methods=["POST"])
def handle_question():
    try:
        data = request.json
        question = data["question"]
        
       
        
        answer_data = rag(question)
        
        result = {
            'question': question,
            'answer': answer_data
        }
        
        db.save_conversation(
            conversation_id=answer_data["conversation_id"],
            question=question,
            answer_data=answer_data,
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500
    
    
@app.route("/feedback", methods=["POST"])
def handle_feedback():
    data = request.json
    conversation_id = data["conversation_id"]
    feedback = data["feedback"]

    if not conversation_id or feedback not in [1, -1]:
        return jsonify({"error": "Invalid input"}), 400

    db.save_feedback(
        conversation_id=conversation_id,
        feedback=feedback,
    )

    result = {
        "message": f"Feedback received for conversation {conversation_id}: {feedback}"
    }
    return jsonify(result)

@app.route("/recent", methods=["GET"])
def recent_conversations():
    limit = request.args.get("limit", default=5, type=int)
    relevance = request.args.get("relevance", default=None, type=str)

    conversations = db.get_recent_conversations(limit=limit, relevance=relevance)

    # Convert rows into serializable dicts
    results = []
    for row in conversations:
        results.append({
            "id": row["id"],
            "question": row["question"],
            "answer": row["answer"],
            "timestamp": row["timestamp"].isoformat(),
            "relevance": row.get("relevance"),
            "feedback": row.get("feedback"),
        })

    return jsonify(results)

@app.route("/feedback_stats", methods=["GET"])
def feedback_stats():
    stats = db.get_feedback_stats()
    return jsonify({
        "thumbs_up": stats["thumbs_up"] or 0,
        "thumbs_down": stats["thumbs_down"] or 0
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)