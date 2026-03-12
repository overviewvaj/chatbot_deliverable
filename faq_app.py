import os
import subprocess
from dotenv import load_dotenv
import streamlit as st
import difflib

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama


# --------------------------------------------------------------------
# 1. LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------------------------
load_dotenv()

api_key = os.getenv("LANGCHAIN_API_KEY")
if not api_key:
    st.error("LANGCHAIN_API_KEY not found. Please check your .env file.")
    st.stop()

api_key = api_key.strip('"').strip("'")
os.environ["LANGCHAIN_API_KEY"] = api_key
os.environ["LANGCHAIN_TRACING_V2"] = "true"


# --------------------------------------------------------------------
# 2. STREAMLIT PAGE SETUP
# --------------------------------------------------------------------
st.set_page_config(page_title="k-ALM Interactive FAQ Bot", page_icon="🤖", layout="centered")
st.title("🤖 k-ALM® AI Chat Assistant")
st.write("Your interactive assistant for k-ALM® modules, ALM topics, and regulatory insights.")


# --------------------------------------------------------------------
# 3. CHECK OLLAMA MODEL
# --------------------------------------------------------------------
def ollama_model_exists(model_name: str) -> bool:
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        return model_name in result.stdout
    except Exception as e:
        st.error(f"Failed to check Ollama models: {e}")
        return False


MODEL_NAME = "llama2:latest"

if not ollama_model_exists(MODEL_NAME):
    st.error(f"Ollama model '{MODEL_NAME}' is missing. Run: `ollama pull llama2:latest`")
    st.stop()


# --------------------------------------------------------------------
# 4. FAQ KNOWLEDGE BASE (Full Dataset)
# --------------------------------------------------------------------
faq_data = {
    "What is k-ALM?":
        "k-ALM® is a cloud-based prudential risk management platform for ICAAP, ILAAP, "
        "stress testing, liquidity risk, IRRBB, FTP, and regulatory reporting.",

    "Which processes does k-ALM support?":
        "k-ALM® supports ICAAP, ILAAP, Recovery & Resolution Planning, Liquidity Stress Testing, "
        "IRRBB, LCR/NSFR reporting, Capital Stress Testing, and Funds Transfer Pricing.",

    "What modules are included in k-ALM?":
        "k-ALM® includes Liquidity Stress Testing (LST), IRRBB, Liquidity Core (LCR/NSFR), "
        "Capital Stress Testing (CST), and Funds Transfer Pricing (FTP).",

    "What is Liquidity Stress Testing?":
        "LST simulates liquidity stress scenarios, calculates OLAR, LCR, NSFR, survival days, "
        "and assesses funding needs under stress.",

    "What is IRRBB?":
        "IRRBB evaluates the sensitivity of a bank’s Economic Value of Equity (EVE) and "
        "Net Interest Income (NII) to interest-rate shocks.",

    "What is the Liquidity Core module?":
        "The Liquidity Core module calculates LCR, NSFR, ALMM and various custom liquidity metrics.",

    "What is FTP?":
        "The Funds Transfer Pricing (FTP) module prices assets and liabilities using matched-maturity "
        "transfer pricing, reflecting market rates, liquidity buffer costs, and capital charges.",

    "What is Capital Stress Testing?":
        "The CST module evaluates capital adequacy under baseline and severe scenarios across 3–5 years.",

    "What are the benefits of k-ALM?":
        "Benefits: regulatory compliance, lower cost, secure single-tenant cloud, expert support, "
        "configurable workflows, and PRA/Basel aligned updates.",

    "Can I export reports from k-ALM?":
        "Yes, reports, dashboards, and raw data can be exported to Excel.",

    "Is k-ALM customizable?":
        "Yes, k-ALM® supports custom assumptions, behavioural models, scenarios, workflows, "
        "and custom risk appetite metrics.",

    "How does k-ALM handle security?":
        "Data is single-tenant, encrypted with AES-256, anonymized before upload, and hosted securely in AWS.",

    "Do you provide training and support?":
        "Yes, onboarding is consultant-led with user guides, workshops, and ongoing expert support.",

    "Which banks is k-ALM designed for?":
        "k-ALM® is designed for small and medium-sized banks seeking robust, regulatory-aligned "
        "ALM and stress testing tools."
}


# --------------------------------------------------------------------
# 5. SMART FAQ MATCHING (Fuzzy + Synonyms + Keyword Logic)
# --------------------------------------------------------------------
def get_faq_answer(query: str) -> str:
    query = query.lower().strip()

    # ✦ Step 1 — Fuzzy matching
    best_match = difflib.get_close_matches(query, faq_data.keys(), n=1, cutoff=0.65)
    if best_match:
        return faq_data[best_match[0]]

    # ✦ Step 2 — Keyword matching
    for question, answer in faq_data.items():
        q_words = question.lower().split()
        if any(word in query for word in q_words):
            return answer

    # ✦ Step 3 — Synonym bridging
    synonyms = {
        "price": ["cost", "fee", "pricing"],
        "security": ["data protection", "safe", "encrypted"],
        "stress": ["scenario", "simulation"],
        "module": ["feature", "component"],
        "support": ["help", "assistance", "training"]
    }

    for question, answer in faq_data.items():
        q_lower = question.lower()
        for main_word, syn_list in synonyms.items():
            if main_word in q_lower and any(syn in query for syn in syn_list):
                return answer

    # Step 4 — No match found
    return "NOT_FOUND"


# --------------------------------------------------------------------
# 6. LLM SETUP (Used Only When Needed)
# --------------------------------------------------------------------
prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are a multi-role assistant for k-ALM®. "
     "Roles you can take: regulatory expert, ALM specialist, liquidity analyst, trainer, onboarding assistant. "
     "You ONLY answer using correct k-ALM information. "
     "If the user asks beyond product scope, give helpful general ALM/guidelines."),
    ("user", "{question}")
])

llm = Ollama(model=MODEL_NAME)
chain = prompt | llm | StrOutputParser()


# --------------------------------------------------------------------
# 7. USER INPUT
# --------------------------------------------------------------------
user_query = st.text_input("Ask me anything about k-ALM, ALM, ICAAP, ILAAP, stress testing, or regulatory topics:")


# --------------------------------------------------------------------
# 8. PROCESS INPUT
# --------------------------------------------------------------------
if user_query:
    faq_answer = get_faq_answer(user_query)

    if faq_answer != "NOT_FOUND":
        # FAQ MATCH FOUND → Respond immediately
        st.success("📘 From FAQ Knowledge Base:")
        st.write(faq_answer)

    else:
        # No FAQ → Use LLM
        with st.spinner("Thinking..."):
            llm_response = chain.invoke({"question": user_query})

        st.info("🤖 AI Expert Response:")
        st.write(llm_response)
