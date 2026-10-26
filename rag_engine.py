
"""CloudPilot retrieval-augmented troubleshooting engine."""

import json
import os
import re
import time
from pathlib import Path

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

EMBEDDING_MODEL = os.getenv(
    "CLOUDPILOT_EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

SIMILARITY_THRESHOLD = float(
    os.getenv("CLOUDPILOT_SIMILARITY_THRESHOLD", "0.30")
)

RETRIEVAL_LIMIT = 3
MAX_GENERATION_ATTEMPTS = 3


# ---------------------------------------------------------
# Load and validate the knowledge base
# ---------------------------------------------------------

def load_knowledge_base():
    """Load and validate troubleshooting records."""
    path = PROJECT_DIR / "knowledge_base.json"

    if not path.exists():
        raise FileNotFoundError(
            f"Knowledge base not found: {path}"
        )

    with path.open("r", encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list) or not records:
        raise ValueError(
            "knowledge_base.json must contain a non-empty JSON list."
        )

    required = {
        "id",
        "provider",
        "service",
        "title",
        "content",
    }

    for index, record in enumerate(records):
        missing = required - record.keys()

        if missing:
            raise ValueError(
                f"Knowledge-base entry {index} is missing fields: "
                f"{', '.join(sorted(missing))}"
            )

        record.setdefault("category", "Other")
        record.setdefault("source_url", "")

    return records


KNOWLEDGE_BASE = load_knowledge_base()

# Load the embedding model once when this module is imported.
EMBEDDER = SentenceTransformer(EMBEDDING_MODEL)

DOCUMENT_TEXTS = [
    (
        f"{item['provider']} {item['service']} "
        f"{item['title']}. {item['content']}"
    )
    for item in KNOWLEDGE_BASE
]

DOCUMENT_EMBEDDINGS = EMBEDDER.encode(
    DOCUMENT_TEXTS,
    convert_to_tensor=True,
    normalize_embeddings=True,
    show_progress_bar=False,
)


# ---------------------------------------------------------
# Text processing
# ---------------------------------------------------------

def tokenize(text):
    """Convert text into lowercase word tokens."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def extract_error_codes(text):
    """Extract HTTP-style status codes, such as 503 and 429."""
    return set(
        re.findall(
            r"\b(?:HTTP\s*)?([1-5]\d{2})\b",
            text,
            flags=re.IGNORECASE,
        )
    )


# ---------------------------------------------------------
# Document retrieval
# ---------------------------------------------------------

def retrieve_documents(
    question,
    limit=RETRIEVAL_LIMIT,
    category=None,
):
    """Rank evidence using semantic, keyword, and error-code matching.

    Adjusted scores are ranking heuristics, not calibrated confidence.
    """
    query = (question or "").strip()

    if not query:
        return []

    candidates = [
        (index, record)
        for index, record in enumerate(KNOWLEDGE_BASE)
        if (
            not category
            or category == "All categories"
            or record["category"] == category
        )
    ]

    if not candidates:
        return []

    query_embedding = EMBEDDER.encode(
        query,
        convert_to_tensor=True,
        normalize_embeddings=True,
    )

    query_tokens = tokenize(query)
    query_error_codes = extract_error_codes(query)

    ranked = []

    aliases = {
        "aws": {"aws", "amazon"},
        "microsoft azure": {"azure", "microsoft"},
        "google cloud": {"google", "gcp"},
        "kubernetes": {"kubernetes", "k8s"},
        "javascript": {"javascript", "js", "node", "nodejs"},
        "rest api": {"api", "rest", "http"},
    }

    for index, record in candidates:
        semantic_score = float(
            util.cos_sim(
                query_embedding,
                DOCUMENT_EMBEDDINGS[index],
            ).item()
        )

        title_tokens = tokenize(record["title"])
        service_tokens = tokenize(record["service"])
        provider_tokens = tokenize(record["provider"])

        title_overlap = query_tokens & title_tokens
        service_overlap = query_tokens & service_tokens
        provider_overlap = query_tokens & provider_tokens

        document_text = (
            f"{record['title']} "
            f"{record['content']} "
            f"{record['service']}"
        )
        document_error_codes = extract_error_codes(document_text)

        # Start with semantic similarity.
        adjusted_score = semantic_score

        # Reward matching words in the document title.
        adjusted_score += min(
            0.18,
            0.045 * len(title_overlap),
        )

        # Reward service and provider matches.
        if service_overlap:
            adjusted_score += 0.08

        if provider_overlap:
            adjusted_score += 0.06

        # Match common provider and technology aliases.
        provider_lower = record["provider"].lower()

        for canonical, words in aliases.items():
            if canonical in provider_lower and query_tokens & words:
                adjusted_score += 0.07
                break

        # Reward exact error-code matches and penalize mismatches.
        if query_error_codes:
            if query_error_codes & document_error_codes:
                adjusted_score += 0.25
            else:
                adjusted_score -= 0.10

        # Keep the score in the 0-to-1 range.
        adjusted_score = max(
            0.0,
            min(1.0, adjusted_score),
        )

        ranked.append(
            {
                "score": semantic_score,
                "adjusted_score": adjusted_score,
                "document": record,
            }
        )

    ranked.sort(
        key=lambda item: item["adjusted_score"],
        reverse=True,
    )

    return ranked[:max(0, limit)]


# ---------------------------------------------------------
# Gemini error classification
# ---------------------------------------------------------

def is_quota_error(error_text):
    """Identify API quota and rate-limit errors."""
    markers = (
        "RESOURCE_EXHAUSTED",
        "QUOTA EXCEEDED",
        "RATE LIMIT",
    )
    return any(marker in error_text.upper() for marker in markers)


def is_temporary_error(error_text):
    """Identify errors that may succeed on a later attempt."""
    markers = (
        "503",
        "504",
        "UNAVAILABLE",
        "DEADLINE_EXCEEDED",
        "INTERNAL",
    )
    return any(marker in error_text.upper() for marker in markers)


# ---------------------------------------------------------
# Gemini answer generation with retries
# ---------------------------------------------------------

def generate_answer(question, sources):
    """Generate a beginner-friendly answer using retrieved evidence."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return (
            "**AI answer generation is unavailable.** Configure "
            "`GEMINI_API_KEY` in your local `.env` file or Streamlit "
            "deployment secrets. The retrieved evidence is shown below."
        )

    if genai is None or types is None:
        return (
            "**AI answer generation is unavailable.** The Google GenAI "
            "SDK is not installed. Install the project dependencies "
            "and try again."
        )

    if not sources:
        return (
            "I couldn't find relevant information in the knowledge base. "
            "Try asking about cloud infrastructure, APIs, Docker, "
            "Kubernetes, or a related troubleshooting issue."
        )

    evidence_parts = []

    for source in sources:
        evidence_parts.append(
            f"[{source['id']}] "
            f"{source['provider']} / {source['service']} — "
            f"{source['title']}\n"
            f"Guidance: {source['content']}\n"
            f"Documentation: "
            f"{source.get('source_url') or 'Not configured'}"
        )

    evidence = "\n\n".join(evidence_parts)

    prompt = f"""You are CloudPilot, a careful technical troubleshooting assistant.
Answer the user's cloud/software troubleshooting question using the retrieved evidence below.

Rules:
- Be beginner-friendly, specific, and practical.
- Use these sections: Likely issue, Checks to perform, If it continues, Limitations.
- Ground recommendations in the provided evidence.
- General diagnostic suggestions are allowed, but clearly label assumptions.
- If the evidence does not fully answer the question, say so.
- Never claim to inspect or change the user's systems.
- Never request passwords, API keys, access tokens, or other secrets.
- Do not invent documentation URLs or claim an unverified action succeeded.
- Recommend checking official documentation before risky production changes.

USER QUESTION:
{question}

RETRIEVED EVIDENCE:
{evidence}
"""

    try:
        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=90000),
        )
    except Exception as exc:
        print(
            "CloudPilot Gemini client initialization failed: "
            f"{type(exc).__name__}"
        )
        return (
            "**AI answer generation is unavailable.** "
            "CloudPilot could not initialize the AI client. "
            "Check your local configuration and deployment logs."
        )

    for attempt in range(MAX_GENERATION_ATTEMPTS):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=700,
                    temperature=0.2,
                ),
            )

            answer = getattr(response, "text", None)

            if answer and answer.strip():
                return answer.strip()

            return (
                "The AI provider returned an empty response. "
                "Please try again."
            )

        except Exception as exc:
            error_text = str(exc).upper()

            # Quota errors will not be fixed by immediate retries.
            quota_error = is_quota_error(error_text)

            if quota_error:
                print(
                    "CloudPilot Gemini quota limit reached. "
                    "Skipping further retries."
                )

                return (
                    "**AI answer generation is temporarily unavailable "
                    "because the Gemini API quota has been reached.** "
                    "Wait for the quota to reset or check your usage "
                    "and limits. Your retrieved troubleshooting evidence "
                    "is still available below."
                )

            temporary_error = is_temporary_error(error_text)

            if (
                temporary_error
                and attempt < MAX_GENERATION_ATTEMPTS - 1
            ):
                wait_seconds = 2 ** (attempt + 1)

                print(
                    "Temporary Gemini service error. "
                    f"Retrying in {wait_seconds} seconds "
                    f"(attempt {attempt + 2}/"
                    f"{MAX_GENERATION_ATTEMPTS})."
                )

                time.sleep(wait_seconds)
                continue

            # Keep technical details out of the public UI.
            print(
                f"CloudPilot Gemini error: "
                f"{type(exc).__name__}: {exc}"
            )

            if temporary_error:
                message = (
                    "The AI service is temporarily unavailable. "
                    "Please try again later."
                )
            else:
                message = (
                    "Check the Gemini model configuration, API access, "
                    "quota, and deployment logs."
                )

            return (
                "**AI answer generation failed.** "
                "The retrieved evidence is still available below. "
                f"{message}\n\n"
                f"Error type: `{type(exc).__name__}`"
            )

    return (
        "**AI answer generation failed.** "
        "The retrieved evidence is still available below."
    )


# ---------------------------------------------------------
# Build the application report
# ---------------------------------------------------------

def build_report(question, category=None):
    """Retrieve evidence and return a structured report."""
    cleaned_question = (question or "").strip()

    if not cleaned_question:
        return {
            "message": "Please enter a question before troubleshooting.",
            "answer": "",
            "sources": [],
        }

    results = retrieve_documents(
        cleaned_question,
        category=category,
    )

    relevant = [
        result
        for result in results
        if result["adjusted_score"] >= SIMILARITY_THRESHOLD
    ]

    if not relevant:
        return {
            "message": (
                "No sufficiently relevant knowledge-base evidence was "
                "found. Try including the technology, service, and "
                "exact error message."
            ),
            "answer": (
                "I couldn't find relevant information in my current "
                "knowledge base. Try asking about cloud infrastructure, "
                "APIs, Docker, Kubernetes, or related troubleshooting."
            ),
            "sources": [],
        }

    sources = []

    for result in relevant:
        document = result["document"]

        sources.append(
            {
                "category": document.get("category", "Other"),
                "provider": document["provider"],
                "service": document["service"],
                "issue": document["title"],
                "steps": document["content"],
                "similarity": result["score"],
                "adjusted_score": result["adjusted_score"],
                "source_id": document["id"],
                "source_url": document.get("source_url", ""),
            }
        )

    answer = generate_answer(
        cleaned_question,
        [result["document"] for result in relevant],
    )

    return {
        "message": (
            f"Found {len(sources)} relevant knowledge-base entr"
            f"{'y' if len(sources) == 1 else 'ies'}."
        ),
        "answer": answer,
        "sources": sources,
    }


# ---------------------------------------------------------
# Optional command-line interface
# ---------------------------------------------------------

if __name__ == "__main__":
    try:
        question = input(
            "Describe your cloud/software issue: "
        ).strip()

        report = build_report(question)

        print("\n" + report["message"] + "\n")

        if report["answer"]:
            print(report["answer"])

        for source in report["sources"]:
            print(
                f"\n[{source['source_id']}] "
                f"{source['provider']} / {source['service']} — "
                f"{source['issue']} "
                f"(relevance {source['adjusted_score']:.3f})"
            )

            if source["source_url"]:
                print(source["source_url"])

    except KeyboardInterrupt:
        print("\nCloudPilot stopped.")
