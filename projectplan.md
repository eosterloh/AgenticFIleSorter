# Agentic Sorter Project Plan

## 1. Project Overview
Plan for this project is to make an agentic sorter of my files
Packages planned on using:
    Watchdog - filesystem monitoring
    pathlib - For making directorys
    shutil - moving files
    asascript - UI stuff
    LangChain - Flexible Agent system(can be used for RAG as well)

Other important systems:
    Ollama - Local cheap llm, no need to get fancy

Resources:
    MacOS python agent: https://dev.to/dilip_muthuraj/building-your-first-ai-agent-on-macos-a-pythonic-journey-4agb
    Anthropic Agent advice: https://www.anthropic.com/engineering/building-effective-agents
    For ingestor and summarizor agents: https://www.freecodecamp.org/news/build-and-deploy-multi-agent-ai-with-python-and-docker/
    Building agents with ollama langchain toolcalling: https://docs.langchain.com/oss/python/integrations/chat/ollama

Model:
    Old = mistral instruct 7B
    New = Llama 3 finetuned for tool coll 8B

Project Structure:

