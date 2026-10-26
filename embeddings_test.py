
from sentence_transformers import SentenceTransformer, util

# Step 1: Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Step 2: Create three example sentences
sentences = [
    "My application is returning HTTP 503.",
    "My website is temporarily unavailable.",
    "How do I change my password?"
]

# Step 3: Convert sentences into embeddings
embeddings = model.encode(sentences, convert_to_tensor=True)

# Step 4: Compare the sentences
similarity_1 = util.cos_sim(embeddings[0], embeddings[1])
similarity_2 = util.cos_sim(embeddings[0], embeddings[2])

# Step 5: Display the similarity scores
print("\n--- CloudPilot Semantic Search Test ---")

print("\nSentence 1:", sentences[0])
print("Sentence 2:", sentences[1])
print("Similarity score:", round(similarity_1.item(), 4))

print("\nSentence 1:", sentences[0])
print("Sentence 3:", sentences[2])
print("Similarity score:", round(similarity_2.item(), 4))
