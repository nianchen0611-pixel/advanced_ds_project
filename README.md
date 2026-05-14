# Personal Finance Copilot

## Project Overview

Personal Finance Copilot is a Streamlit-based personal finance analysis app powered by a local LLM backend through Ollama. The app allows users to ask natural-language questions about their transaction data. The local LLM helps understand the user's question and selects the appropriate finance tool, while deterministic Python tools compute the actual financial results.

The main idea of this project is to combine LLM-based natural-language interaction with reliable tool-grounded financial calculations. Instead of asking the LLM to calculate numbers directly, the app uses Python tools to compute results from the dataset and then presents the answer in a user-friendly way.

---

## Pure LLM vs Tool-only vs Tool-calling

This project responds to the core framing of comparing pure LLM, tool-only, and tool-calling approaches for personal finance analysis.

| Approach | Strength | Limitation |
|---|---|---|
| Pure LLM | Flexible natural-language interaction | May hallucinate numerical answers |
| Tool-only System | Accurate deterministic calculations | Limited conversational flexibility |
| Tool-calling Copilot | Combines LLM interaction with grounded tool outputs | Requires orchestration between LLM and tools |

Our final implementation focuses on the tool-calling approach. The local LLM is responsible for understanding user intent and selecting the appropriate financial analysis tool, while deterministic Python modules compute grounded financial results.

---

## Final System Workflow

```text
User Question
→ Local Ollama LLM interprets the request
→ LLM selects the appropriate finance tool
→ Deterministic Python tool computes the result
→ The app generates a grounded financial response
→ Streamlit displays the final answer
```

The LLM is used for natural-language understanding and tool selection. The actual financial calculations are performed by deterministic Python tools, which helps reduce hallucination and numerical errors.

---

## Key Features

- Load and preview personal transaction data from a CSV file
- Show basic dataset overview, including:
  - Total transactions
  - Expense transactions
  - Income transactions
  - Average transaction amount
- Manually look up spending by selected month and category
- Ask natural-language finance questions through the LLM Copilot
- Use a local Ollama LLM backend instead of relying on external API calls
- Route user questions to deterministic finance tools
- Display the selected tool and deterministic tool result for transparency
- Support common personal finance questions, such as:
  - Which month had the highest expense?
  - Which month had the highest income?
  - Which category did I spend the most on?
  - Which month did I spend most on Cafe?
  - How much did I spend on Cafe in April 2025?
  - Were there any unusual expenses?
  - How do my income and expenses compare over time?
  - Which expense categories should I monitor more carefully?

---

## How the App Works

The system follows a tool-grounded LLM workflow:

```text
User question
→ Local Ollama LLM selects a finance tool
→ Deterministic Python tool computes the result
→ The app generates a grounded answer from the tool result
```

The LLM is used for:
- Natural-language understanding
- Tool selection
- Response formatting

The deterministic backend is responsible for:
- Numerical computation
- Data lookup
- Financial aggregation
- Validation logic

This separation reduces hallucination risk and improves reproducibility.

---

## Project Structure

```text
personal-finance-copilot/
│
├── app.py                    # Main Streamlit app
├── llm_client.py             # Local Ollama LLM client
├── llm_copilot.py            # LLM tool routing and answer pipeline
├── finance_tools.py          # Finance analysis tools
├── anomaly_detection.py      # Global and category-relative anomaly detection
├── budget_tools.py           # Budget-related helper functions
├── preprocessing.py          # Data loading and preprocessing
├── ui_style.py               # Custom Streamlit styling
├── combined_transactions.csv # Default sample transaction dataset
├── requirements.txt          # Python dependencies
├── .gitignore                # Files excluded from GitHub
└── README.md                 # Project documentation
```

---

## Dataset Format

The app expects a transaction CSV file with the following required columns:

```text
date, type, category, amount
```

Optional columns include:

```text
account, currency, description
```

Example:

```csv
date,type,category,amount,account,currency,description
2025-08-20,Expense,Cafe,8,acct_3,BYN,tag_1
2025-08-17,Expense,Cafe,20,acct_1,BYN,tag_1
2025-09-01,Income,Salary,3000,acct_1,BYN,tag_2
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/nianchen0611-pixel/advanced_ds_project.git
cd advanced_ds_project
```

### 2. Create and activate a virtual environment

For macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

For Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Python dependencies

```bash
python -m pip install -r requirements.txt
```

---

## Local LLM Setup with Ollama

This project uses Ollama to run a local LLM backend.

### 1. Install Ollama

Download and install Ollama from:

```text
https://ollama.com
```

After installation, check that Ollama is available:

```bash
ollama --version
```

### 2. Pull the local model

This project uses `qwen2.5:3b` as the local LLM model:

```bash
ollama pull qwen2.5:3b
```

You can test the model with:

```bash
ollama run qwen2.5:3b
```

Then type:

```text
Say hello in one sentence.
```

If the model responds, the local LLM is working.

To exit Ollama chat, type:

```text
/bye
```

---

## Environment Variables

Create a `.env` file in the project folder:

```bash
touch .env
```

Add the following line:

```env
OLLAMA_MODEL=qwen2.5:3b
```

Do not upload `.env` to GitHub.

---

## Running the App

Run the Streamlit app:

```bash
python -m streamlit run app.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

---

## Example Questions

You can ask the Copilot questions such as:

```text
Which month had the highest expense?
Which month had the highest income?
Which category did I spend the most on?
Which month did I spend most on Cafe?
How much did I spend on Cafe in April 2025?
Were there any unusual expenses?
How do my income and expenses compare over time?
Which expense categories should I monitor more carefully?
```

---

## Main Tools Used in the App

The app uses deterministic Python tools to compute financial results. These tools include:

- Monthly income and expense comparison
- Highest expense month detection
- Highest income month detection
- Top expense category detection
- Category-specific monthly spending lookup
- Transaction amount summary
- Income-expense comparison
- Anomaly detection
- Categories-to-monitor recommendation

The LLM does not directly calculate these values. Instead, it selects the appropriate tool, and the Python backend computes the answer.

---

## Notes and Limitations

- This app uses a local LLM backend through Ollama with `qwen2.5:3b`.
- The project uses a pretrained local LLM for inference, not local fine-tuning.
- Numerical calculations are performed by deterministic Python tools, not directly by the LLM.
- The local LLM is mainly used for natural-language understanding and tool selection.
- For exact financial numbers, the app uses tool-grounded outputs and deterministic templates to reduce hallucination and formatting errors.
- Smaller local models may be less stable than larger API-based models for strict JSON tool routing.
- This app is a personal finance analysis prototype and should not be treated as professional financial advice.

---

## Course Project Context

This project was developed for an Advanced Data Science course. Compared with the Milestone 2 version, the final version adds local LLM calls through Ollama, tool routing, and tool-grounded answer generation to address the project’s original pure LLM vs tool-calling framing.

The final version focuses on:

- Local LLM-powered tool-calling workflow
- Transparent deterministic financial analysis
- Tool-grounded response generation
- Local deployment through Ollama
- Reducing hallucination in financial question answering

---

## Authors

- Peter
- Angela

