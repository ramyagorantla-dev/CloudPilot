# CloudPilot ☁️ — AI-Powered Cloud Troubleshooting Assistant

CloudPilot is a Retrieval-Augmented Generation (RAG) application that helps users troubleshoot common cloud infrastructure, API, DevOps, and runtime issues. It retrieves relevant troubleshooting knowledge using semantic search and uses Google's Gemini model to generate responses grounded in the retrieved evidence.

**Live Demo:** https://cloudpilot.streamlit.app  
**GitHub Repository:** https://github.com/ramyagorantla-dev/CloudPilot

## Key Features

- **Semantic Search:** Uses Sentence Transformers embeddings to find troubleshooting information relevant to a user's question.
- **RAG-Based Responses:** Combines knowledge retrieval with Gemini-generated answers grounded in retrieved documentation.
- **Relevance Filtering:** Filters retrieved entries using a configurable relevance threshold.
- **Hybrid Retrieval Ranking:** Combines semantic similarity with keyword, service, alias, and error-code signals.
- **Source-Grounded Guidance:** Presents relevant knowledge-base entries and supporting documentation links.
- **Out-of-Scope Handling:** Avoids treating unrelated questions as supported troubleshooting requests.
- **Evaluation Without API Calls:** Includes a retrieval evaluation script that tests search quality without consuming Gemini API quota.

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| User Interface | Streamlit |
| Semantic Retrieval | Sentence Transformers |
| Embedding Model | `sentence-transformers/all-MiniLM-L6-v2` |
| Generative AI | Google Gemini API |
| Knowledge Base | JSON |
| Testing | Python-based retrieval evaluation |
| Deployment | Streamlit Community Cloud |

## Architecture

1. **User Query:** The user submits a troubleshooting question through the Streamlit interface.
2. **Embedding:** CloudPilot represents the question using a Sentence Transformers embedding model.
3. **Retrieval and Ranking:** The application ranks knowledge-base entries using semantic similarity and additional relevance signals.
4. **Relevance Filtering:** Entries below the configured threshold are excluded.
5. **Answer Generation:** Gemini generates troubleshooting guidance using the retrieved evidence, when the API is available and within quota.
6. **Results:** The interface presents the response and supporting knowledge-base sources.

## Evaluation

CloudPilot's retrieval evaluation was run against five test questions:

| Test scenario | Result |
|---|---|
| Kubernetes `CrashLoopBackOff` | Pass |
| Website returning HTTP 503 | Pass |
| Azure virtual machine RDP connection failure | Pass |
| Docker container repeatedly restarting | Pass |
| Unrelated restaurant reservation question | Pass — correctly found no relevant source |

**Retrieval evaluation: 5/5 tests passed.**

These results evaluate retrieval behavior, not the factual accuracy of generated answers or the complete end-to-end RAG pipeline. Gemini answer generation requires a valid API key and available API quota.

Run the retrieval evaluation locally with:

```bash
python evaluate.py
```

## Knowledge Base

The starter knowledge base covers selected topics across:

- **Cloud infrastructure:** AWS, Microsoft Azure, and Google Cloud
- **Programming and runtime:** Python, Java, and JavaScript
- **DevOps:** Kubernetes, Docker, Linux, Git, and CI/CD
- **Databases and APIs:** SQL, MySQL, and REST APIs
- **AI applications:** LLM API quotas, RAG retrieval, embeddings, and grounding

Coverage depends on the entries actually present in the knowledge base. It is a prototype and does not support every platform or error.

## Run Locally

### Prerequisites

- Python 3.11 or newer recommended
- Git
- A Gemini API key for AI-generated answers

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/ramyagorantla-dev/CloudPilot.git
   cd CloudPilot
   ```

2. Create and activate a virtual environment.

   **Windows PowerShell:**

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Configure your Gemini API key in a local `.env` file:

   ```env
   GEMINI_API_KEY=your_gemini_api_key
   ```

   Never commit `.env` or expose your API key publicly.

5. Start the application:

   ```bash
   python -m streamlit run app_web.py
   ```

6. Open the local URL displayed in the terminal.

Retrieval can be evaluated without calling Gemini by running `python evaluate.py`. Generating AI answers requires a valid API key and available quota.

## Configuration

CloudPilot supports the following configuration options where implemented:

- `GEMINI_API_KEY` — API key used for Gemini answer generation.
- `GEMINI_MODEL` — optional Gemini model override.
- `CLOUDPILOT_SIMILARITY_THRESHOLD` — retrieval relevance threshold; default is `0.30`.
- `CLOUDPILOT_EMBEDDING_MODEL` — optional embedding model override.

Check the application configuration for the active model default and any additional supported settings.

## Limitations and Responsible Use

- Retrieval scores are ranking signals, not calibrated confidence probabilities.
- The knowledge base is limited and manually curated.
- AI-generated answers may be incomplete or incorrect; verify recommendations against current official documentation.
- CloudPilot does not connect to cloud accounts, inspect live infrastructure, or execute remediation commands.
- Gemini availability and response generation depend on API quota and service availability.

## Future Improvements

- Expand the troubleshooting knowledge base.
- Improve retrieval quality with additional test cases and relevance analysis.
- Evaluate generated answers for factual grounding and correctness.
- Add more robust error handling and observability.
- Explore integrations with cloud monitoring and diagnostic tools.

## Project Purpose

CloudPilot is a learning and portfolio project exploring semantic search, Retrieval-Augmented Generation, prompt grounding, and the development of AI-powered troubleshooting applications.
