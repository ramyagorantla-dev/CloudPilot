
import json
import re

# Load the troubleshooting knowledge base
with open("knowledge_base.json", "r", encoding="utf-8") as file:
    knowledge_base = json.load(file)


def search_knowledge_base(question):
    stop_words = {
        "why", "what", "how", "is", "my", "the", "a",
        "an", "i", "to", "for", "in", "on", "and",
        "do", "does", "can", "could", "me", "of"
    }

    question_words = set(
        re.findall(r"\b[a-z0-9]+\b", question.lower())
    ) - stop_words

    scored_results = []

    for document in knowledge_base:
        title_words = set(
            re.findall(r"\b[a-z0-9]+\b", document["title"].lower())
        )
        service_words = set(
            re.findall(r"\b[a-z0-9]+\b", document["service"].lower())
        )
        content_words = set(
            re.findall(r"\b[a-z0-9]+\b", document["content"].lower())
        )

        score = (
            len(question_words & title_words) * 3
            + len(question_words & service_words) * 3
            + len(question_words & content_words)
        )

        if score > 0:
            scored_results.append((score, document))

    scored_results.sort(key=lambda item: item[0], reverse=True)

    return scored_results[:2]


def main():
    question = input("CloudPilot: Describe your cloud issue: ")
    results = search_knowledge_base(question)

    print("\n--- CloudPilot Troubleshooting Results ---")

    if results:
        for score, document in results:
            print("\nService:", document["service"])
            print("Issue:", document["title"])
            print("Relevance score:", score)
            print("Guidance:", document["content"])
    else:
        print("No matching guidance found.")
        print("Try mentioning the service or error message.")


if __name__ == "__main__":
    main()
