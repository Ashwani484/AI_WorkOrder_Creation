1. Project Architecture & Component Map
The system consists of four primary layers:

Interface Layer (FastAPI): Receives the chat query.

Extraction Layer (Pydantic + LLM): Maps unstructured text to a rigid SAP-ready schema.

Logic Layer (LangGraph): Manages the state and decides if we have enough info to proceed.

Integration Layer (OData/REST): Communicates with SAP/HANA.



-> Prerequisites
Install Libraries: pip install fastapi uvicorn streamlit pandas plotly langchain-openai langgraph requests.

API Key: Set your OPENAI_API_KEY environment variable so the agent can process natural language.

-> Execution Steps
Terminal 1: Launch Mock SAP Service

Command: uvicorn SAP_dummy:app --port 8080.

Purpose: Simulates the backend ERP system that generates WOXXXXX IDs and provides processing statuses.

Terminal 2: Launch Backend & Orchestrator

Command: uvicorn main:app --port 8000.

Purpose: Runs the LangGraph "brain" that extracts incident details and sanitizes data for the JSON archive.

Terminal 3: Launch User Interface

Command: streamlit run streamlit_app.py.

Purpose: Opens the premium dashboard at http://localhost:8501 for logging incidents and viewing analytics.

-> Quick Verification
Check Status: Look at the sidebar in Streamlit; all systems should show Connected ✅.

Create Order: Enter a query like "LAN is down at ODC-9 Lucknow, Priority-1" in the Operations tab.

Search: Use the Global Search in the main body to view the structured data for your new WO number.

Clean Database: If old records with backticks cause search errors, delete work_orders_db.json and start fresh.