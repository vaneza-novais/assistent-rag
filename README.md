meu-assistente-rag/
├── data/
│   └── raw/                 # Seus documentos de estudo (PDFs, textos)
├── src/
│   ├── __init__.py
│   ├── chunking.py          # Semana 3 — suas funções de chunking na mão
│   ├── retrieval.py         # Semana 4 — embeddings + FAISS + chamada ao LLM
│   ├── pipeline.py          # Semana 5 — versão com LangChain
│   └── agent.py             # Semana 6 — versão com LangGraph
├── evaluation/               # Fase 3 — scripts com Ragas
├── app/                      # Fase 5 — Streamlit/Gradio, quando for expor o assistente
├── .env.example
├── requirements.txt
└── README.md
