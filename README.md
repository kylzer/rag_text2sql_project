
# Mekari Assignment Test

This is a challenge test from Mekari.  
An Fraud Knowledge Agent

# Requirements
- Docker
- Docker Compose
- Python 3.10

**NOTES** : .env is not ignored for test purpose
# Specification
For this challenge, I use Macbook Pro M1 with 8GB RAM and 512GB Storage.

That's the reason I don't use GPU on Docker Compose for Ollama.

# Model
- nomic-embed-text-v1.5 for Embedding (use sentence-transformers/all-MiniLM-L6-v2 for Low-end PC)
- GPT-OSS 20B for Generative (with Ollama)

# Tool List
- fraud_knowledge


# Library & Frameworks
## For Main Program
```
chonkie==1.5.0
docling==2.65.0
gradio==6.1.0
langchain==1.2.0
langchain-core==1.2.4
langchain-google-genai==4.1.2
langchain-openai==1.1.6
mlx-vlm==0.3.9
python-dotenv==1.1.0
rich==14.2.0
weaviate==0.1.2
weaviate-client==4.19.0
```
## For Embedding
```
einops==0.8.1
fastapi==0.115.0
uvicorn==0.34.0
sentence-transformers>=3.0.0
pydantic==2.10.0
numpy>=1.26.0
torch>=2.2.0
```

# Installation
Clone the project

```bash
  git clone https://github.com/kylzer/mekari_test.git
```

Go to the project directory

```bash
  cd mekari_test
```

Run with Makefile
```bash
  make run
```

Logging Container  
Embedding Service Logs
```
  docker logs -f embedding_service
```
Weaviate Logs
```
  docker logs -f mekari_test-weaviate-1 
```

# Usage
```
1. Up Docker Container
2. Open Gradio in a browser
3. If there is no changes, you can access by open [Here](http://localhost:7860/)
4. You can do indexing or upsert the document first.
5. You can parse the .csv into .sql (if the table and headers is same, then it will concat)
6. After "Upserting Successful", you can try Retrieval
```

# Photo
TBD
# Video
TBD