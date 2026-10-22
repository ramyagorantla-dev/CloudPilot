
import json
from sentence_transformers import SentenceTransformer, util

# 1. Load our troubleshooting knowledge
with open("knowledge_base.json", "r", encoding="utf-8") as file:
    knowledge_base = json.load(file)

# 2. Load the local embedding model
print("Loading CloudPilot knowledge...")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# 3. Convert knowledge records into embeddings
documents = [
    f"{item['service']}: {item['title']}. {item['content']}"
    for item in knowledge_base
]

document_embeddings = model.encode(
    documents,
    convert_to_tensor=True
)


def retrieve_documents(question, limit=2):
    """Find knowledge records most similar to the question."""
    question_embedding = model.encode(
        question,
        convert_to_tensor=True
    )

    scores = util.cos_sim(
        question_embedding,
        document_embeddings
    )[0]

    top_results = scores.topk(k=min(limit, len(knowledge_base)))

    results = []

    for score, index in zip(
        top_results.values.tolist(),
        top_results.indices.tolist()
    ):
        results.append({
            "score": float(score),
            "document": knowledge_base[index]
        })

    return results


def build_report(question):
    """Build a troubleshooting report from retrieved evidence."""
    results = retrieve_documents(question)
    relevant_results = [
    result for result in results
    if result["score"] >= 0.35
]

    if not relevant_results:
        return {
            "question": question,
            "message": (
                "I could not find sufficiently similar guidance "
                "in the knowledge base. Try providing the service "
                "name or exact error message."
            ),
            "sources": []
        }

    guidance = []

    for result in relevant_results:
        document = result["document"]

        guidance.append({
            "service": document["service"],
            "issue": document["title"],
            "steps": document["content"],
            "similarity": round(result["score"], 3),
            "source_id": document["id"]
        })

    return {
        "question": question,
        "message": (
            "Here is the troubleshooting guidance retrieved "
            "from the CloudPilot knowledge base. Verify these "
            "checks against your actual environment."
        ),
        "sources": guidance
    }


if __name__ == "__main__":
    question = input("\nCloudPilot: Describe your cloud issue: ")

    report = build_report(question)

    print("\n========== CLOUDPILOT REPORT ==========")
    print("\nQuestion:", report["question"])
    print("\nAssessment:", report["message"])

    for source in report["sources"]:
        print("\nService:", source["service"])
        print("Issue:", source["issue"])
        print("Recommended checks:", source["steps"])
        print("Similarity:", source["similarity"])
        print("Knowledge source ID:", source["source_id"])

    print("\n=======================================")
