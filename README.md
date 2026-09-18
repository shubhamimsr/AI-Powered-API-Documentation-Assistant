# APIMind AI — AI-Powered API Documentation Assistant

> An AI-powered Retrieval-Augmented Generation (RAG) assistant that lets developers query OpenAPI/Swagger documentation using natural language, with Model Context Protocol (MCP) integration for use from tools such as VS Code Copilot.

<!-- 🎬 QUICK GLIMPSE — top-of-README preview banner. Replace src paths with your actual screenshots/GIF. -->
<p align="center">
  <!-- <img src="docs/images/hero-banner.png" alt="APIMind AI demo preview" width="850"> -->
  <img width="940" height="529" alt="image" src="https://github.com/user-attachments/assets/bf4536e2-ff76-4448-bc1f-b2780794f830" alt="APIMind AI demo preview" width="850"/>

</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/6932212e-42b7-478b-9676-fd0fd0ebf99d" alt="FastAPI Swagger UI" width="270">
  <!-- <img width="940" height="529" alt="image" src="https://github.com/user-attachments/assets/6932212e-42b7-478b-9676-fd0fd0ebf99d" /> -->

  <img src="https://github.com/user-attachments/assets/42e5f1aa-f387-4283-b834-a81fff146aba" alt="VS Code Copilot using APIMind MCP tool" width="270">
  <!-- <img width="940" height="888" alt="image" src="https://github.com/user-attachments/assets/42e5f1aa-f387-4283-b834-a81fff146aba" /> -->

  <img src="https://github.com/user-attachments/assets/98abbd8c-b9ed-4fd8-94bb-3d3efd6724c8" alt="Hybrid RAG retrieval logs" width="270">
  <!-- <img width="1856" height="781" alt="image" src="https://github.com/user-attachments/assets/98abbd8c-b9ed-4fd8-94bb-3d3efd6724c8" /> -->

</p>

<p align="center"><em>👇 Full walkthrough and setup below.</em></p>

---

## 🚀 Project Overview

Developers often work with multiple API specifications spread across different OpenAPI/Swagger YAML or JSON files. Finding the correct endpoint, HTTP method, authentication details, request structure, and response information can become time-consuming.

**APIMind AI** solves this problem by ingesting API documentation into a searchable knowledge base and using a hybrid RAG pipeline to retrieve relevant documentation before asking an LLM to generate a grounded answer.

The project also exposes selected capabilities through an **MCP server**, allowing MCP-compatible clients such as VS Code Copilot to discover project files and ask questions about the uploaded API documentation.

### Example questions

```text
Which endpoint creates a customer?

How do I retrieve a specific GitHub repository?

What authentication does the Stripe API use?

Which endpoint creates a payment?

What HTTP method is used to update a repository?

Is there an endpoint for listing available models?
```

If the uploaded documentation does not contain enough evidence, the system is designed to respond with an appropriate **"I don't know"** response instead of relying on outside knowledge.

---

# 🏗️ Architecture

The system consists of two major flows:

### Document ingestion

```text
OpenAPI / Swagger YAML or JSON
              │
              ▼
       FastAPI Upload API
              │
              ▼
        Parser Service
              │
              ▼
      Semantic Chunking
              │
              ▼
       Embedding Service
              │
              ▼
       OpenAI Embeddings
              │
              ▼
     PostgreSQL + pgvector
```

### Question answering / RAG

```text
User Question
      │
      ▼
   Chat API
      │
      ▼
 Query Rewriting
      │
      ▼
Document Resolution
      │
      ▼
 ┌───────────────────────┐
 │   Hybrid Retrieval    │
 │                       │
 │ Vector Search         │
 │ Keyword Search        │
 └───────────┬───────────┘
             │
             ▼
      RRF Fusion
             │
             ▼
 Cross-Encoder Reranking
             │
             ▼
    Top-K Relevant Chunks
             │
             ▼
    Confidence Scoring
             │
             ▼
      Prompt Construction
             │
             ▼
        Groq LLM
             │
             ▼
   Grounding Verification
             │
             ▼
       Final Answer
```

---

# 🧠 RAG Pipeline

The core of APIMind AI is a hybrid RAG pipeline.

## 1. Document parsing

Uploaded OpenAPI/Swagger YAML or JSON files are parsed into structured API information.

The system extracts information such as:

- Endpoint
- HTTP method
- API description
- Request information
- Response information
- Authentication details
- Parameters
- API-specific documentation

---

## 2. Semantic chunking

Instead of treating an entire API specification as one large document, the documentation is divided into meaningful chunks.

Example:

```text
POST /customers
Creates a new customer...
Request:
...
Response:
...
```

Metadata is retained with every chunk:

```text
document_id
source_file
chunk_type
endpoint
method
chunk_text
embedding
```

---

## 3. Embeddings

The chunks are converted into vector embeddings.

The project uses an external embedding model through the embedding service and stores the resulting vectors in PostgreSQL using **pgvector**.

---

## 4. Hybrid retrieval

APIMind does not depend only on semantic similarity.

It performs two retrieval strategies:

### Semantic / Vector Search

Uses pgvector similarity search to find conceptually related documentation.

### Keyword Search

Uses PostgreSQL Full-Text Search to find exact terminology and API-specific keywords.

The two result sets are combined using:

### Reciprocal Rank Fusion (RRF)

```text
Vector Results
       +
Keyword Results
       │
       ▼
   RRF Fusion
       │
       ▼
Unified Ranking
```

---

## 5. Cross-Encoder reranking

The fused results are passed through a Cross-Encoder reranker.

Current model:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

This provides a second-stage relevance check between:

```text
Question ↔ Retrieved Documentation
```

The highest-ranked chunks are then passed to the LLM.

---

## 6. Confidence scoring

Before generating an answer, the retrieved context is evaluated using the project's confidence mechanism.

If the retrieved evidence is insufficient, the system avoids generating an unsupported answer.

Example:

```text
I couldn't find enough evidence in the uploaded documentation
to answer this question.
```

---

## 7. Grounding verification

Generated answers can also be checked against the retrieved documentation.

The grounding verifier evaluates whether the answer is supported by the supplied context.

The goal is to reduce hallucinated API information.

---

# 🤖 LLM

The project uses the OpenAI-compatible client interface with:

```text
Groq API
openai/gpt-oss-20b
```

The LLM receives:

- System instructions
- User question
- Conversation history
- Retrieved documentation

The prompt explicitly instructs the model to use only the supplied documentation.

---

# 🔌 MCP Integration

APIMind also includes a **Model Context Protocol (MCP) server**.

The MCP server exposes selected project capabilities as tools that can be consumed by MCP-compatible clients.

The primary tool is:

# ⭐ `ask_api_documentation`

This is the main MCP tool for APIMind.

It allows an MCP client such as VS Code Copilot to ask questions about the indexed API documentation.

Conceptually:

```text
VS Code Copilot
       │
       ▼
MCP Client
       │
       ▼
APIMind MCP Server
       │
       ▼
ask_api_documentation
       │
       ▼
FastAPI / RAG Backend
       │
       ▼
Hybrid RAG Pipeline
       │
       ▼
Grounded API Answer
```

---

# 🛠️ MCP Tools

## 1. `ask_api_documentation` ⭐

**Purpose:** Ask questions about the uploaded API documentation.

This is the primary APIMind MCP capability.

Example:

```text
Which endpoint creates a Stripe customer?
```

or:

```text
How do I retrieve a specific GitHub repository?
```

The tool sends the question through the APIMind RAG pipeline and returns the documentation-grounded result.

### Recommended usage

In VS Code Copilot, ask naturally:

```text
Use APIMind to tell me which endpoint creates a customer.
```

or:

```text
Ask the API documentation what HTTP method is used to retrieve a GitHub repository.
```

The MCP client can invoke the tool when appropriate.

---

## 2. `list_project_files`

**Purpose:** List files available inside the configured MCP workspace.

Example:

```text
List the project files available to me.
```

The tool returns the files/directories visible within the configured workspace.

It is protected by workspace path validation.

---

## 3. `read_project_file`

**Purpose:** Read the contents of a text file inside the configured MCP workspace.

Example:

```text
Read the OpenAPI file github.yaml.
```

The MCP server validates that the requested path remains inside the configured workspace.

Binary files and files exceeding the configured maximum file size are rejected.

---

## 4. `hello_tool`

A simple MCP connectivity/demo tool.

Example:

```text
Use the hello tool with the name Developer.
```

Expected response:

```text
Hello Developer, welcome to APIMind MCP Server!
```

This tool is mainly useful for verifying that the MCP server is connected correctly.

---

# ⚠️ About `generate_code`

A `generate_code` MCP tool may exist in experimental/development code, but **the dedicated code-generation service has not been implemented as part of the current RAG backend**.

Therefore, it is intentionally **not considered a supported APIMind feature** in this README.

The current supported workflow is:

```text
Question
   ↓
ask_api_documentation
   ↓
RAG Retrieval
   ↓
Grounded Documentation Answer
```

Code generation can be added later as a dedicated service with its own retrieval and code-generation prompt.

---

# 💻 Using APIMind with VS Code Copilot

The project includes an MCP server that can be connected to an MCP-compatible client such as VS Code Copilot.

## 1. Start the FastAPI backend

From the project root:

```bash
uvicorn app.main:app --reload
```

The FastAPI application will expose the APIMind REST APIs.

Swagger UI is normally available at:

```text
http://127.0.0.1:8000/docs
```

---

## 2. Start the MCP server

Navigate to the MCP server directory:

```bash
cd mcp_server
```

Start the server:

```bash
python server.py
```

The current MCP server uses:

```text
127.0.0.1:8000
```

and Streamable HTTP transport.

> If your FastAPI application and MCP server are configured to use the same port, configure one of them to use another port before starting both simultaneously.

---

## 3. Connect the MCP server to VS Code

Use VS Code's MCP configuration / MCP-compatible tooling to register the APIMind MCP server.

Once connected, the available tools should include:

```text
hello_tool
list_project_files
read_project_file
ask_api_documentation
```

The exact UI may vary depending on your VS Code and Copilot version.

---

# 🧪 Example VS Code Copilot Prompts

After connecting the MCP server, try:

### API documentation

```text
Use ask_api_documentation to find the endpoint that creates a Stripe customer.
```

### GitHub API

```text
Use ask_api_documentation to explain how to retrieve a specific GitHub repository.
```

### Authentication

```text
Use ask_api_documentation to tell me what authentication mechanism is documented for the Stripe API.
```

### File listing

```text
Use list_project_files to show the files available in the workspace.
```

### Reading a file

```text
Use read_project_file to read github.yaml.
```

### Combined workflow

```text
First inspect the available project files, then use APIMind to answer:
Which endpoint is used to create a repository?
```

---

# 📡 REST API Endpoints

The FastAPI backend provides the core application functionality.

Typical capabilities include:

| Endpoint / Capability | Purpose |
|---|---|
| `POST /upload` | Upload an OpenAPI/Swagger document |
| `POST /chat` | Ask a documentation question |
| Streaming chat | Stream an LLM response |
| Document management | List, inspect and delete uploaded documents |
| Code generation | Not currently implemented as a supported backend service |

> Refer to the automatically generated FastAPI Swagger documentation for the exact current endpoint paths and request/response schemas.

---

# 🗄️ Database

APIMind uses PostgreSQL.

The database stores:

```text
uploaded_documents
document_chunks
conversations
messages
```

`document_chunks` contains the vector embeddings used for semantic retrieval.

### pgvector

pgvector enables similarity search directly inside PostgreSQL.

### PostgreSQL Full-Text Search

PostgreSQL's full-text search is used as the keyword retrieval component of the hybrid retrieval pipeline.

---

# 🔐 Safety and Guardrails

The project includes several mechanisms to reduce unsafe or unsupported responses.

### Documentation-only prompting

The LLM is instructed to answer using only retrieved documentation.

### Confidence threshold

Insufficient retrieval evidence can result in an explicit fallback response.

### Grounding verification

Generated answers can be checked against retrieved context.

### MCP workspace protection

Filesystem tools validate requested paths against the configured workspace.

### File-size protection

Large files are rejected by the filesystem reader according to the configured limit.

---

# 📁 Project Structure

A simplified structure looks like:

```text
AI_API_Documentation_QnA/
│
├── app/
│   ├── api/
│   ├── database/
│   ├── services/
│   │   ├── chat_service.py
│   │   ├── retrieval_service.py
│   │   ├── vector_service.py
│   │   ├── embedding_service.py
│   │   ├── reranker_service.py
│   │   ├── query_rewriter.py
│   │   ├── confidence_service.py
│   │   ├── document_resolver.py
│   │   ├── ingestion_service.py
│   │   └── llm_service.py
│   │
│   ├── prompts/
│   ├── config.py
│   └── main.py
│
├── mcp_server/
│   ├── server.py
│   ├── tools/
│   │   ├── filesystem.py
│   │   └── ...
│   ├── utils/
│   │   └── path_utils.py
│   └── config.py
│
├── requirements.txt
├── .env
└── README.md
```

---

# ⚙️ Technology Stack

| Category | Technology |
|---|---|
| Language | Python |
| API Framework | FastAPI |
| Database | PostgreSQL |
| Vector Database | pgvector |
| LLM Provider | Groq |
| LLM | openai/gpt-oss-20b |
| Embeddings | External embedding model |
| Reranking | Sentence Transformers Cross-Encoder |
| API Documentation | OpenAPI / Swagger |
| RAG | Hybrid Retrieval |
| MCP | Model Context Protocol |
| MCP Transport | Streamable HTTP |
| Client Integration | VS Code / Copilot |
| ORM / DB Access | SQLAlchemy |

---

# 📸 Project Glimpses

Add screenshots from your implementation here.

Recommended screenshots:

### 1. FastAPI Swagger UI


<p align="center">
  <img src="https://github.com/user-attachments/assets/d480f9fc-2610-40bb-aa59-39fccd71d589" alt="FastAPI Swagger UI" width="700">
  <!-- <img width="940" height="529" alt="image" src="https://github.com/user-attachments/assets/d480f9fc-2610-40bb-aa59-39fccd71d589" /> -->

</p>

### 2. RAG Retrieval Logs


<p align="center">
  <img src="https://github.com/user-attachments/assets/191fb68f-1e8f-4b0e-8a9e-4051c03b559f" alt="RAG Retrieval Logs" width="700">
  <!-- <img width="940" height="396" alt="image" src="https://github.com/user-attachments/assets/191fb68f-1e8f-4b0e-8a9e-4051c03b559f" /> -->

</p>

### 3. MCP Inspector


<p align="center">
  <!-- <img src="docs/images/mcp-inspector.png" alt="MCP Inspector showing available tools" width="700"> -->
  <img alt="image" src="https://github.com/user-attachments/assets/45c81625-4cb3-4585-bb0c-673b72a9d6d7" width="270" />
  <img alt="image" src="https://github.com/user-attachments/assets/dac0c296-223c-4346-bfa6-2203aa3f9c54" width="270"/>
  <img alt="image" src="https://github.com/user-attachments/assets/fdbc53d2-f921-42bb-aa3d-022825a4ad9c" width="270"/>
  <img alt="image" src="https://github.com/user-attachments/assets/d0a0124e-c8d5-4e47-a654-a7117e4726b1" width="270"/>
  <img alt="image" src="https://github.com/user-attachments/assets/3fdb8b8f-9fcb-473b-b75c-5483d449c48a" width="270"/>
  <img alt="image" src="https://github.com/user-attachments/assets/45bc4694-32d1-4bde-99d8-496bed9cd025" width="270"/>
</p>

### 4. VS Code Copilot + MCP

<p align="center">
  <!-- <img src="docs/images/vscode-mcp.png" alt="VS Code Copilot invoking ask_api_documentation" width="700"> -->
  <img width="940" height="228" alt="image" src="https://github.com/user-attachments/assets/b6bdf942-aac7-48cd-8f5d-1803a3de456a" />
  <img width="940" height="888" alt="image" src="https://github.com/user-attachments/assets/9e4d81fd-ebd9-4dd8-97fb-7f8e38b02ea5" />

</p>

### 5. PostgreSQL + pgvector


<p align="center">
  <!-- <img src="docs/images/database.png" alt="PostgreSQL pgvector indexed document chunks" width="700"> -->
  <img width="940" height="384" alt="uploaded documents" src="https://github.com/user-attachments/assets/caf41d95-124d-46db-ac1c-b9a3b22b1a66" />
  <img width="940" height="492" alt="uploaded documents' chunking" src="https://github.com/user-attachments/assets/55abf2ee-5159-436d-a24d-9ff804b0c0ee" />
  <img width="940" height="455" alt="chunk's embeddings" src="https://github.com/user-attachments/assets/41ce1261-22d2-4063-a4e9-bb6ed6f98f33" />

</p>

### Glimpse of other MCP tool calls 

<p align="center">
  <!-- <img src="docs/images/database.png" alt="PostgreSQL pgvector indexed document chunks" width="700"> -->

  <img width="940" height="722" alt="hello_tool" src="https://github.com/user-attachments/assets/4ab6e284-4871-4bb2-ab46-4bfe37ab8cf1" />
  <img width="940" height="507" alt="list_project_files" src="https://github.com/user-attachments/assets/89572d7a-514f-425d-af71-567c4fbed8c4" />
  <img width="985" height="969" alt="read_project_file" src="https://github.com/user-attachments/assets/6fabc265-c1ee-47e1-b5ca-172e00142e6d" />
</p>

---

# 🚀 Future Enhancements

The current implementation focuses on the RAG + MCP foundation.

Possible future improvements:

- Dedicated `generate_code` service
- Language-specific code generation
- Better API authentication extraction
- More advanced document routing
- Multi-document reasoning
- Evaluation datasets and retrieval metrics
- Automated RAG evaluation
- Additional MCP tools
- Authentication and user-level access control
- Production deployment

---

# 🎯 Project Highlights

APIMind demonstrates practical implementation of:

- **Retrieval-Augmented Generation**
- **Hybrid Search**
- **Vector Similarity Search**
- **PostgreSQL Full-Text Search**
- **Reciprocal Rank Fusion**
- **Cross-Encoder Reranking**
- **Query Rewriting**
- **Automatic Document Resolution**
- **Confidence Scoring**
- **Grounding Verification**
- **LLM Integration**
- **Model Context Protocol**
- **MCP Tool Development**
- **FastAPI**
- **PostgreSQL + pgvector**

The main objective is to make API documentation **searchable, contextual, and accessible directly from developer tooling** while keeping generated answers grounded in the uploaded documentation.

---

## 👨‍💻 Author

**Shubham Raskar**

AI / Backend Engineering Project

---

## 📌 Status

### Core RAG

**Completed**

### MCP Integration

**Completed**

### `ask_api_documentation`

**Primary MCP tool — supported**

### Filesystem MCP tools

**Supported**

### Code Generation

**Future enhancement**

---

> **APIMind AI — Ask your API documentation instead of searching through it.**
