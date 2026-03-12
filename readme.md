# **PDF-Based Retrieval-Augmented Generation (RAG) Chatbot**



### **1. Overview**



**This project implements a PDF-only Retrieval-Augmented Generation (RAG) chatbot that answers user queries strictly based on the contents of provided PDF documents.**



**The system is designed for accuracy, auditability, and operational efficiency, using:**



* **Persistent vector storage**
* **Controlled document reprocessing**
* **Deterministic LLM behavior**
* **Centralized logging**



**Two Streamlit applications are provided:**

* **ui\_bot\_main.py – standard user-facing chatbot**
* **main\_app.py – enhanced application with admin-controlled vector store refresh**



### **2. Key Guarantees**

* **Answers are grounded strictly in PDF data**
* **No hallucination when content is missing**
* **Vector store is persistent across runs**
* **PDF reprocessing is controlled and explicit**
* **All events are logged**



### **3. High-Level Architecture**



**PDF Files**

**↓**

**PDF Loader (PyMuPDF)**

**↓**

**Text Chunking**

**↓**

**SentenceTransformer Embeddings**

**↓**

**ChromaDB (Persistent Vector Store)**

**↓**

**Semantic Retriever**

**↓**

**Context-Only Prompt**

**↓**

**Groq LLM (LLaMA 3.1, temperature=0)**

**↓**

**Streamlit UI**



### **4. Core Components**



**processing\_n\_text\_splitting.py**

* **Discovers and loads PDFs**
* **Adds metadata (source\_file, file\_type)**
* **Splits content into overlapping chunks**



**embedding\_manager.py**

* **Loads SentenceTransformer (all-MiniLM-L6-v2)**
* **Generates embeddings for documents and queries**



**vector.py**

* **Persistent ChromaDB vector store**
* **Reuses existing embeddings by default**
* **Supports incremental refresh**



* **rag\_retriever.py**
* **Converts queries to embeddings**
* **Performs similarity search**
* **Filters results using similarity thresholds**



* **llm\_manager.py**
* **Initializes Groq LLM**
* **Uses deterministic settings (temperature = 0.0)**
* **Requires GROQ\_API\_KEY**



**rag\_pipeline.py**

* **Combines retriever and LLM**
* **Builds context-only prompts**
* **Returns:**

	**Answer**

	**Source metadata**

&nbsp;	**Confidence score**



### **5. Streamlit Applications**



**ui\_bot\_main.py (Standard User Interface)**



**Purpose**

**A lightweight chatbot UI for end users.**



**Behavior**



* **Initializes the RAG pipeline**
* **Loads PDFs and embeddings on first run (cached)**
* **Answers user queries using retrieved PDF context**
* **Maintains chat history via Streamlit session state**



**Use Case**



* **Read-only querying**
* **Non-admin users**
* **Simple deployments**



**main\_app.py (Admin-Enabled Application)**



**Purpose**

**An enhanced Streamlit application designed for operational control and scalability.**



#### **5.1 Persistent Vector Store Access (Key Feature)**



**Unlike ui\_bot\_main.py, main\_app.py does NOT re-embed PDFs on every application run.**



**Instead:**



* **It directly accesses the existing ChromaDB vector store**
* **Embeddings and tokenization are reused**
* **Startup time is significantly reduced**



#### **5.2 “Refresh Vector Store” Button (Admin-Controlled)**



**A dedicated UI control allows explicit vector store refresh:**


**🔄 Refresh Vector Store**



**Behavior**



* **Re-processes PDFs**
* **Re-generates embeddings**
* **Updates the persistent vector store**
* **Only triggered when:**
* 
**&nbsp;	The button is clicked, OR The vector store is empty**



**Design Intent**



* **Prevent accidental or repeated re-embedding**
* **Ensure controlled updates when PDFs change**
* **Suitable for admin-only privileges**



#### **5.3 Typical Execution Flow**

**Scenario				Behavior**

**App starts			Loads existing vector store**

**Vector store exists		No reprocessing**

**Vector store empty		PDFs processed automatically**

**Admin clicks refresh		PDFs reprocessed and embeddings updated**



### **6. Hallucination Control (Critical)**



**What Happens If PDFs Lack Information?**



**Example query:**



**“How do I calculate NSFR or LCR?”**



**If the PDFs do not contain this information:**



* **Retriever returns no relevant chunks**
* **LLM is not prompted with external knowledge**
* **Response is: No relevant information found.**



This design prevents hallucination by construction, not by instruction alone.



### 7\. Logging \& Observability



What Is Logged?



* Application startup
* Vector store initialization
* PDF processing
* Embedding generation
* Vector refresh button clicks
* User queries 
* LLM responses



Each run generates a timestamped log file in /log\_file.



### 8\. Environment Setup



Create a .env file:



GROQ\_API\_KEY=your\_groq\_api\_key\_here



### 9\. How to Run

Standard UI

streamlit run ui\_bot\_main.py



Admin-Enabled UI

streamlit run main\_app.py



### 10\. Intended Use Cases



* Regulatory document analysis
* Financial reporting support (PDF-grounded)
* Internal policy assistants
* Audit-safe enterprise RAG systems



### 11\. Limitations (Explicit \& Intentional)



* No external knowledge usage
* No hallucinated calculations
* No automatic PDF reprocessing
* Accuracy depends on PDF content quality



### System Flow Diagram



#### High-Level End-to-End Flow



┌───────────────────────┐

│      User (UI)        		 │

│  (Streamlit Chat UI)  		 │

└───────────┬───────────┘

&nbsp;           │

&nbsp;           │ User Query

&nbsp;           ▼

┌───────────────────────┐

│   RAG Pipeline        		 │

│  (rag\_pipeline.py)    		 │

└───────────┬───────────┘

&nbsp;           │

&nbsp;           │ Query

&nbsp;           ▼

┌───────────────────────┐

│  RAG Retriever        		 │

│ (rag\_retriever.py)    		 │

└───────────┬───────────┘

&nbsp;           │

&nbsp;           │ Query Embedding

&nbsp;           ▼

┌───────────────────────┐

│ Embedding Manager     	  	 │

│ (embedding\_manager.py)		 │

└───────────┬───────────┘

&nbsp;           │

&nbsp;           │ Vector Search

&nbsp;           ▼

┌───────────────────────┐

│  Vector Store         		 │

│ (ChromaDB, Persistent)		 │

│   (vector.py)         		 │

└───────────┬───────────┘

&nbsp;           │

&nbsp;           │ Relevant Chunks

&nbsp;           ▼

┌───────────────────────┐

│ Context Builder       		 |

│ (Top-K PDF Chunks)    		 |

└───────────┬───────────┘

&nbsp;           │

&nbsp;           │ Context-only Prompt

&nbsp;           ▼

┌───────────────────────┐

│   Groq LLM            		 │

│ (llm\_manager.py)     			 │

│  LLaMA-3.1           			 │

└───────────┬───────────┘

&nbsp;           │

&nbsp;           │ Answer

&nbsp;           ▼

┌───────────────────────┐

│  Streamlit UI         		 │

│  (Displayed to User) 			 │

└───────────────────────┘





#### Vector Store Initialization \& Refresh Flow (Admin Logic)



┌─────────────────────────────┐

│ Application Startup         			 │

│ (main\_app.py)              			 │

└─────────────┬───────────────┘

&nbsp;             	   │

&nbsp;             	   ▼

┌─────────────────────────────┐

│ Load Persistent Vector Store			 │

│ (ChromaDB)                  			 │

└─────────────┬───────────────┘

&nbsp;             	  │

&nbsp;    ┌────────┴────────┐

&nbsp;    │                 		  │

&nbsp;    ▼                	      ▼

Vector Store Exists?   	      No

&nbsp;    │               		  │

&nbsp;    │              		  ▼

&nbsp;    │       ┌─────────────────────┐

&nbsp;    │       │ Load \& Split PDFs   			│

&nbsp;    │       │ (processing\_n\_...)   		│

&nbsp;    │       └───────────┬─────────┘

&nbsp;    │                   	  │

&nbsp;    │                   	  ▼

&nbsp;    │       ┌─────────────────────┐

&nbsp;    │       │ Generate Embeddings 			│

&nbsp;    │       │ (EmbeddingManager) 			│

&nbsp;    │       └───────────┬─────────┘

&nbsp;    │                   	  │

&nbsp;    │                   	  ▼

&nbsp;    │       ┌─────────────────────┐

&nbsp;    │       │ Update Vector Store 			│

&nbsp;    │       │ (vector.py)         		    │

&nbsp;    │       └─────────────────────┘

&nbsp;    │

&nbsp;    ▼

┌─────────────────────────────┐

│ RAG Pipeline Ready          			 │

└─────────────────────────────┘



#### Admin “Refresh Vector Store” Button Flow



┌─────────────────────────────┐

│ Admin Clicks Refresh Button 			 │

│ (Streamlit UI)            			 │

└─────────────┬───────────────┘

&nbsp;            	   │

&nbsp;             	   ▼

┌─────────────────────────────┐

│ Reprocess PDFs              	  		 │

│ (processing\_n\_text\_...)     			 │

└─────────────┬───────────────┘

&nbsp;             	   │

&nbsp;                  ▼

┌─────────────────────────────┐

│ Regenerate Embeddings       			 │

│ (EmbeddingManager)          			 │

└─────────────┬───────────────┘

&nbsp;                  │

&nbsp;                  ▼

┌─────────────────────────────┐

│ Update Persistent          			 │

│ Vector Store (ChromaDB)     			 │

└─────────────┬───────────────┘

&nbsp;                  │

&nbsp;                  ▼

┌─────────────────────────────┐

│ RAG Pipeline Continues      			 │

│ with Updated Knowledge Base 			 │

└─────────────────────────────┘

&nbsp;	

#### 

#### Hallucination Control Flow (Important)



User Query

&nbsp;  │

&nbsp;  ▼

Retriever Finds Relevant Chunks?

&nbsp;  │

&nbsp;┌─┴───────────────┐

&nbsp;│                 		  │

Yes               	  No

&nbsp;│                 	      │

&nbsp;▼                 	  ▼

LLM Uses Context   "No relevant information found"

&nbsp;│

&nbsp;▼

Grounded Answer







