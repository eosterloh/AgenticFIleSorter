# Agentic Sorter

An autonomous agent that sorts files on your machine using an LLM.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
# Run one-time startup sort
python sorteragentV1.py --startup

# Run passive watchdog sorter
python sorteragentV1.py --passive
```