PDF-Based Retrieval-Augmented Generation (RAG) Chatbot

1. Overview

This project implements a PDF-only Retrieval-Augmented Generation (RAG) chatbot that answers user queries strictly based on the contents of provided PDF documents.

The system is designed for accuracy, auditability, and operational efficiency, using:

Persistent vector storage
Controlled document reprocessing
Deterministic LLM behavior
Centralized logging

Two Streamlit applications are provided:
ui_bot_main.py – standard user-facing chatbot
main_app.py – enhanced application with admin-controlled vector store refresh

2. Key Guarantees
Answers are grounded strictly in PDF data
No hallucination when content is missing
Vector store is persistent across runs
PDF reprocessing is controlled and explicit
All events are logged

3. High-Level Architecture

PDF Files
↓
PDF Loader (PyMuPDF)
↓
Text Chunking
↓
SentenceTransformer Embeddings
↓
ChromaDB (Persistent Vector Store)
↓
Semantic Retriever
↓
Context-Only Prompt
↓
Groq LLM (LLaMA 3.1, temperature=0)
↓
Streamlit UI

4. Core Components

processing_n_text_splitting.py
Discovers and loads PDFs
Adds metadata (source_file, file_type)
Splits content into overlapping chunks

embedding_manager.py
Loads SentenceTransformer (all-MiniLM-L6-v2)
Generates embeddings for documents and queries

vector.py
Persistent ChromaDB vector store
Reuses existing embeddings by default
Supports incremental refresh

rag_retriever.py
Converts queries to embeddings
Performs similarity search
Filters results using similarity thresholds

llm_manager.py
Initializes Groq LLM
Uses deterministic settings (temperature = 0.0)
Requires GROQ_API_KEY

rag_pipeline.py
Combines retriever and LLM
Builds context-only prompts
Returns:
	Answer
	Source metadata
	Confidence score

5. Streamlit Applications

ui_bot_main.py (Standard User Interface)

Purpose
A lightweight chatbot UI for end users.

Behavior

Initializes the RAG pipeline
Loads PDFs and embeddings on first run (cached)
Answers user queries using retrieved PDF context
Maintains chat history via Streamlit session state

Use Case

Read-only querying
Non-admin users
Simple deployments

main_app.py (Admin-Enabled Application)

Purpose
An enhanced Streamlit application designed for operational control and scalability.

5.1 Persistent Vector Store Access (Key Feature)

Unlike ui_bot_main.py, main_app.py does NOT re-embed PDFs on every application run.

Instead:

It directly accesses the existing ChromaDB vector store
Embeddings and tokenization are reused
Startup time is significantly reduced

5.2 “Refresh Vector Store” Button (Admin-Controlled)

A dedicated UI control allows explicit vector store refresh:

🔄 Refresh Vector Store

Behavior

Re-processes PDFs
Re-generates embeddings
Updates the persistent vector store
Only triggered when:
	The button is clicked, OR The vector store is empty

Design Intent

Prevent accidental or repeated re-embedding
Ensure controlled updates when PDFs change
Suitable for admin-only privileges

5.3 Typical Execution Flow
Scenario				Behavior
App starts			Loads existing vector store
Vector store exists		No reprocessing
Vector store empty		PDFs processed automatically
Admin clicks refresh		PDFs reprocessed and embeddings updated

6. Hallucination Control (Critical)

What Happens If PDFs Lack Information?

Example query:

“How do I calculate NSFR or LCR?”

If the PDFs do not contain this information:

Retriever returns no relevant chunks
LLM is not prompted with external knowledge
Response is: No relevant information found.

This design prevents hallucination by construction, not by instruction alone.

7. Logging & Observability

What Is Logged?

Application startup
Vector store initialization
PDF processing
Embedding generation
Vector refresh button clicks
User queries 
LLM responses

Each run generates a timestamped log file in /log_file.

8. Environment Setup

Create a .env file:

GROQ_API_KEY=your_groq_api_key_here

9. How to Run
Standard UI
streamlit run ui_bot_main.py

Admin-Enabled UI
streamlit run main_app.py

10. Intended Use Cases

Regulatory document analysis
Financial reporting support (PDF-grounded)
Internal policy assistants
Audit-safe enterprise RAG systems

11. Limitations (Explicit & Intentional)

No external knowledge usage
No hallucinated calculations
No automatic PDF reprocessing
Accuracy depends on PDF content quality

System Flow Diagram

High-Level End-to-End Flow

┌───────────────────────┐
│      User (UI)        		 │
│  (Streamlit Chat UI)  		 │
└───────────┬───────────┘
            │
            │ User Query
            ▼
┌───────────────────────┐
│   RAG Pipeline        		 │
│  (rag_pipeline.py)    		 │
└───────────┬───────────┘
            │
            │ Query
            ▼
┌───────────────────────┐
│  RAG Retriever        		 │
│ (rag_retriever.py)    		 │
└───────────┬───────────┘
            │
            │ Query Embedding
            ▼
┌───────────────────────┐
│ Embedding Manager     	  	 │
│ (embedding_manager.py)		 │
└───────────┬───────────┘
            │
            │ Vector Search
            ▼
┌───────────────────────┐
│  Vector Store         		 │
│ (ChromaDB, Persistent)		 │
│   (vector.py)         		 │
└───────────┬───────────┘
            │
            │ Relevant Chunks
            ▼
┌───────────────────────┐
│ Context Builder       		 |
│ (Top-K PDF Chunks)    		 |
└───────────┬───────────┘
            │
            │ Context-only Prompt
            ▼
┌───────────────────────┐
│   Groq LLM            		 │
│ (llm_manager.py)     			 │
│  LLaMA-3.1           			 │
└───────────┬───────────┘
            │
            │ Answer
            ▼
┌───────────────────────┐
│  Streamlit UI         		 │
│  (Displayed to User) 			 │
└───────────────────────┘


Vector Store Initialization & Refresh Flow (Admin Logic)

┌─────────────────────────────┐
│ Application Startup         			 │
│ (main_app.py)              			 │
└─────────────┬───────────────┘
              	   │
              	   ▼
┌─────────────────────────────┐
│ Load Persistent Vector Store			 │
│ (ChromaDB)                  			 │
└─────────────┬───────────────┘
              	  │
     ┌────────┴────────┐
     │                 		  │
     ▼                	      ▼
Vector Store Exists?   	      No
     │               		  │
     │              		  ▼
     │       ┌─────────────────────┐
     │       │ Load & Split PDFs   			│
     │       │ (processing_n_...)   		│
     │       └───────────┬─────────┘
     │                   	  │
     │                   	  ▼
     │       ┌─────────────────────┐
     │       │ Generate Embeddings 			│
     │       │ (EmbeddingManager) 			│
     │       └───────────┬─────────┘
     │                   	  │
     │                   	  ▼
     │       ┌─────────────────────┐
     │       │ Update Vector Store 			│
     │       │ (vector.py)         		    │
     │       └─────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│ RAG Pipeline Ready          			 │
└─────────────────────────────┘

Admin “Refresh Vector Store” Button Flow

┌─────────────────────────────┐
│ Admin Clicks Refresh Button 			 │
│ (Streamlit UI)            			 │
└─────────────┬───────────────┘
             	   │
              	   ▼
┌─────────────────────────────┐
│ Reprocess PDFs              	  		 │
│ (processing_n_text_...)     			 │
└─────────────┬───────────────┘
              	   │
                   ▼
┌─────────────────────────────┐
│ Regenerate Embeddings       			 │
│ (EmbeddingManager)          			 │
└─────────────┬───────────────┘
                   │
                   ▼
┌─────────────────────────────┐
│ Update Persistent          			 │
│ Vector Store (ChromaDB)     			 │
└─────────────┬───────────────┘
                   │
                   ▼
┌─────────────────────────────┐
│ RAG Pipeline Continues      			 │
│ with Updated Knowledge Base 			 │
└─────────────────────────────┘
	

Hallucination Control Flow (Important)

User Query
   │
   ▼
Retriever Finds Relevant Chunks?
   │
 ┌─┴───────────────┐
 │                 		  │
Yes               	  No
 │                 	      │
 ▼                 	  ▼
LLM Uses Context   "No relevant information found"
 │
 ▼
Grounded Answer


