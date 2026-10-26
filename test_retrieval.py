
from rag_engine import retrieve_documents

question = "My website is returning HTTP 503"

results = retrieve_documents(question)

print("\n===== CloudPilot Retrieval Test =====")
print("Question:", question)

for result in results:
    score = result["adjusted_score"]
    title = result["document"]["title"]

    print(f"Score: {score:.3f} | {title}")
