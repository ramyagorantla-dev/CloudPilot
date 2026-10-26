
from rag_engine import retrieve_documents

test_cases = [
    {
        "question": "My EC2 instance is unreachable",
        "expected": "AWS001",
    },
    {
        "question": "I cannot connect to my virtual server",
        "expected": "AWS001",
    },
    {
        "question": "I cannot access my files in cloud storage",
        "expected": "AWS002",
    },
    {
        "question": "S3 is denying access to my objects",
        "expected": "AWS002",
    },
    {
        "question": "How do I investigate application errors in logs?",
        "expected": "AWS003",
    },
    {
        "question": "Where can I find my application's error logs?",
        "expected": "AWS003",
    },
    {
        "question": "My application returns HTTP 503",
        "expected": "AWS004",
    },
    {
        "question": "My website shows service unavailable",
        "expected": "AWS004",
    },
]

passed = 0
total = len(test_cases)

print("\n=== CloudPilot Retrieval Evaluation ===")

for test in test_cases:
    results = retrieve_documents(test["question"])

    actual = (
        results[0]["document"]["id"]
        if results
        else "NO RESULT"
    )

    success = actual == test["expected"]

    if success:
        passed += 1

    print(f"\nQuestion: {test['question']}")
    print(f"Expected: {test['expected']}")
    print(f"Retrieved: {actual}")
    print(f"Result: {'PASS' if success else 'FAIL'}")

accuracy = (passed / total) * 100

print("\n=== Evaluation Summary ===")
print(f"Passed: {passed}/{total}")
print(f"Top-result accuracy: {accuracy:.1f}%")
