
# RAG and Text2SQL Project (Fraud Detection)

An end-to-end Fraud Knowledge Agent built using Retrieval-Augmented Generation (RAG),
vector search, and Text-to-SQL to answer questions over both unstructured documents
and structured databases.

# Requirements
- Docker
- Docker Compose
- Python 3.10
- Ollama

**NOTES** : .env is not ignored for test purpose
# Specification
For this challenge, I use Macbook Pro M1 with 8GB RAM and 512GB Storage.

That's the reason I don't use GPU on Docker Compose for Ollama.

# Model
- nomic-embed-text-v1.5 for Embedding (use sentence-transformers/all-MiniLM-L6-v2 for Low-end PC)
- GPT-OSS 20B for Generative (with Ollama)
- SmolDocling-MLX for VLM (Parsing PDF to MD "txt")

**NOTES** : Feel free to change the VLM Model (this model only works for Apple Silicon chips)
**NOTES** : I don't provide Ollama in Docker Compose in purpose (can't do Embedding and LLM at the same device)
# Tool List
- fraud_knowledge
- database_information
- fraud_database


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
  git clone https://github.com/kylzer/rag_text2sql_project.git
```

Go to the project directory

```bash
  cd rag_text2sql_project
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
  docker logs -f rag_text2sql_project-weaviate-1 
```

# Usage
```
1. Do `make run`
2. Open Gradio in a browser
3. If there is no changes, you can access by open [Here](http://localhost:7860/)
4. You can do indexing or upsert the document first.
5. You can parse the .csv into .sql (if the table and headers is same, then it will concat)
6. After "Upserting Successful", you can try Retrieval
```

# Photo

## Indexing
### Main
![Indexing Main](assets/photos/Indexing%20Main.png)

### Input
![Indexing Input](assets/photos/Indexing%20Input.png)

### Loading
![Indexing Process](assets/photos/Indexing%20Process.png)
![Indexing Processing](assets/photos/Indexing%20Processing.png)

### Status
![Indexing Success](assets/photos/Indexing%20Success.png)

## CSV to SQL
### Main
![CSV to SQL Main](assets/photos/CSV%20to%20SQL%20Main.png)

### Input
![CSV to SQL Input](assets/photos/CSV%20to%20SQL%20Input.png)

### Result
![CSV to SQL Stored](assets/photos/CSV%20to%20SQL%20Stored.png)
![CSV to SQL Stored 2](assets/photos/CSV%20to%20SQL%20Stored%202.png)
![CSV to SQL Concatted CSV](assets/photos/CSV%20to%20SQL%20Concatted%20CSV.png)

## Retrieval
### Main
![Retrieval Main](assets/photos/Retrieval%20Main.png)

### Loading
![Retrieval Loading](assets/photos/Retrieval%20Loading.png)

### Result
![Retrieval Result 1](assets/photos/Retrieval%20Result%201.png)
![Retrieval Result 2](assets/photos/Retrieval%20Result%202.png)


# Video
TBD