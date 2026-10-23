# CloudPilot ☁️

### AI-Powered Cloud Troubleshooting Assistant

CloudPilot is a Python-based cloud troubleshooting assistant that uses semantic search and retrieval-based techniques to identify relevant troubleshooting guidance for common cloud issues.

## Features

- **Semantic Search:** Finds relevant troubleshooting information based on the meaning of a user's question.
- **Evidence-Based Guidance:** Retrieves troubleshooting steps from a structured knowledge base.
- **Interactive Web Interface:** Provides a simple interface built with Streamlit.
- **Retrieval Evaluation:** Includes a script to evaluate whether expected troubleshooting records are retrieved.
- **Automated Tests:** Includes tests for the initial knowledge-base search functionality.

## Technology Stack

- Python
- Streamlit
- Sentence Transformers
- PyTorch
- JSON
- Git and GitHub

## How It Works

1. The user describes a cloud-related problem.
2. CloudPilot converts the question into an embedding.
3. Semantic search compares the question with the knowledge-base records.
4. Relevant troubleshooting guidance is retrieved.
5. The web interface displays the results and their similarity scores.

## Run Locally

Clone this repository and navigate into the project folder:

```bash
git clone https://github.com/ramyagorantla-dev/CloudPilot
cd CloudPilot
```

Create and activate a virtual environment, then install the dependencies:

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Start the web application:

```bash
python -m streamlit run app_web.py
```

## Evaluation

Run the retrieval evaluation script:

```bash
python evaluate_cloudpilot.py
```

Run the available automated tests:

```bash
python -m pytest -q
```

## Current Scope and Future Improvements

The current version uses local embedding models and a small troubleshooting knowledge base. It retrieves existing guidance and presents an evidence-based report; it does not yet use an LLM to generate answers.

Planned improvements include expanding the knowledge base, improving retrieval evaluation, adding optional LLM-based answer generation, and deploying a public demo using a free hosting option where supported.

## Cost

The current local workflow does not require paid LLM API calls. Hosting and resource costs will depend on the deployment platform and its current free-tier limits.

## Disclaimer

CloudPilot is an educational project. Always verify troubleshooting recommendations against your organization's policies and official cloud-provider documentation before making infrastructure changes.
