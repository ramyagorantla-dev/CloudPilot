
import json
from sentence_transformers import SentenceTransformer, util

# Step 1: Load the knowledge base
with open("knowledge_base.json", "r", encoding="utf-8") as file:
    knowledge_base = json.load(file)

# Step 2: Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Step 3: Prepare searchable text for every document
documents = []

for item in knowledge_base:
    text = (
        item["service"] + ". " +
        item["title"] + ". " +
        item["content"]
    )
    documents.append(text)

# Step 4: Convert all documents into embeddings
document_embeddings = model.encode(
    documents,
    convert_to_tensor=True
)

print("CloudPilot semantic search is ready!")
print("Knowledge base records:", len(documents))

# Step 5: Ask the user for a cloud problem
question = input("\nDescribe your cloud issue: ")

# Step 6: Convert the question into an embedding
question_embedding = model.encode(
    question,
    convert_to_tensor=True
)

# Step 7: Compare the question with all documents
scores = util.cos_sim(
    question_embedding,
    document_embeddings
)[0]

# Step 8: Rank documents by similarity
top_k = min(3, len(documents))
top_results = scores.topk(top_k)

# Step 9: Display the best matches
print("\n--- CloudPilot Semantic Search Results ---")

for score, index in zip(
    top_results.values,
    top_results.indices
):
    result = knowledge_base[index.item()]

    print("\nService:", result["service"])
    print("Issue:", result["title"])
    print("Similarity:", round(score.item(), 4))
    print("Guidance:", result["content"])
