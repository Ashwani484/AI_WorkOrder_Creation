1. Project Architecture & Component Map
The system consists of four primary layers:

Interface Layer (FastAPI): Receives the chat query.

Extraction Layer (Pydantic + LLM): Maps unstructured text to a rigid SAP-ready schema.

Logic Layer (LangGraph): Manages the state and decides if we have enough info to proceed.

Integration Layer (OData/REST): Communicates with SAP/HANA.