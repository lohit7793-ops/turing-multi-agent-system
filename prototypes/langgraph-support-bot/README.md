## LangGraph Customer Support Bot (prototype)

### Run (Windows, PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py

### What it does
Tiny stateful customer-support bot built with LangGraph. Routes FAQs, creates refund/ticket flows, and escalates to human handoff when needed.
