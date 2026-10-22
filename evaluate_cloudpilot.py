
from rag_engine import retrieve_documents

# Test questions and the expected top result
test_cases = [
    {
        "question": "My EC2 instance is unreachable",
        "expected": "AWS001",
    },
    {
        "question": "I cannot access my files in cloud storage",
        "expected": "AWS002",
    },
    {
        "question": "How do I investigate application errors in logs?",
        "expected": "AWS003",
    },
    {
        "question": "My application returns HTTP 503",
        "expected": "AWS004",
    },
]

passed = 0

print("\n=== CloudPilot Retrieval Evaluation ===")

for test in test_cases:
    results = retrieve_documents(test["question"])

    if results:
        actual = results[0]["document"]["id"]
    else:
        actual = "NO RESULT"

    success = actual == test["expected"]

    if success:
        passed += 1

    print(f"\nQuestion: {test['question']}")
    print(f"Expected: {test['expected']}")
    print(f"Retrieved: {actual}")
    print(f"Result: {'PASS' if success else 'FAIL'}")

total = len(test_cases)
accuracy = (passed / total) * 100

print("\n=== Evaluation Summary ===")
print(f"Passed: {passed}/{total}")
print(f"Top-result accuracy: {accuracy:.1f}%")
