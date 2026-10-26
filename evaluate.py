
from rag_engine import (
    retrieve_documents,
    SIMILARITY_THRESHOLD,
)

test_questions = [
    "My Kubernetes pod is stuck in CrashLoopBackOff",
    "My website is returning HTTP 503",
    "I cannot connect to my Azure virtual machine using RDP",
    "How do I troubleshoot a Docker container that keeps restarting?",
    "How do I change my restaurant reservation?",
]

print("\n===== CloudPilot Retrieval Evaluation =====\n")
print("Mode: Retrieval only (Gemini API is not called)\n")

passed = 0
failed = 0

for question in test_questions:
    print(f"Question: {question}")

    try:
        results = retrieve_documents(question)

        relevant = [
            result
            for result in results
            if result["adjusted_score"] >= SIMILARITY_THRESHOLD
        ]

        print(f"Sources found: {len(relevant)}")

        if relevant:
            top_result = relevant[0]
            document = top_result["document"]

            print("Top source:", document["title"])
            print(
                "Ranking score:",
                f"{top_result['adjusted_score']:.3f}",
            )

            # For the first four questions, we expect a relevant
            # troubleshooting source in the current knowledge base.
            if "restaurant reservation" not in question.lower():
                passed += 1
                print("Retrieval result: PASS")
            else:
                print(
                    "Retrieval result: REVIEW "
                    "(question may be outside the knowledge base)"
                )
        else:
            if "restaurant reservation" in question.lower():
                passed += 1
                print(
                    "Retrieval result: PASS "
                    "(no relevant source for out-of-scope question)"
                )
            else:
                failed += 1
                print("Retrieval result: FAIL (no relevant source)")

        print("-" * 60)

    except Exception as error:
        failed += 1
        print("ERROR:", error)
        print("-" * 60)

print("\n===== Evaluation Summary =====")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print("Gemini requests made: 0")
