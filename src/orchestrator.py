from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage
from src.schema import WorkOrderSchema
from src.sap_service import SAPConnector
from src.llm import init_llm

class AgentState(TypedDict):
    messages: List[BaseMessage]
    extracted_data: Optional[WorkOrderSchema]
    final_response: Optional[str]

# Initialize structured LLM
llm = init_llm("openAI")
structured_llm = llm.with_structured_output(WorkOrderSchema)

def extraction_node(state: AgentState):
    """
    Extracts data and validates that no mandatory fields are empty.
    If fields are missing, it returns a request for clarification.
    """
    try:
        # LLM attempts to parse the full message history into the schema
        results = structured_llm.invoke(state["messages"])
        
        # Define mandatory fields based on the industrial schema
        mandatory_fields = ["intent", "problem_area", "severity", "location_id", "summary"]
        missing = []

        # Programmatically check each field[cite: 3]
        for field in mandatory_fields:
            value = getattr(results, field, None)
            if value is None or (isinstance(value, str) and not value.strip()):
                # Format field names for user readability (e.g., location_id -> location id)
                missing.append(field.replace("_", " "))

        if missing:
            # Loop-back logic: Return the question to the user via final_response[cite: 3, 5]
            fields_str = ", ".join(missing)
            return {
                "extracted_data": None, 
                "final_response": f"I have captured some details, but I still need: **{fields_str}** to create the work order. Could you please provide those?"
            }
        
        # All fields present: proceed to next node[cite: 3]
        return {"extracted_data": results, "final_response": None}

    except Exception:
        return {
            "extracted_data": None, 
            "final_response": "I'm having trouble categorizing this request. Please provide the Site Name, Problem, and Severity."
        }

def sap_execution_node(state: AgentState):
    """Calls the SAP tool and formats the final dashboard response[cite: 1, 3]."""
    sap = SAPConnector()
    data = state["extracted_data"]
    
    # Send validated data to SAP/Mock service[cite: 1, 4]
    result = sap.create_work_order(data)
    
    if result["status"] == "success":
        # Format a premium Markdown response for the Streamlit dashboard[cite: 3, 5]
        msg = (f"✅ **Work Order Created Successfully**\n\n"
               f"- **Work Order ID:** `{result['order_id']}`\n"
               f"- **Processing Status:** {result['sap_status']}\n"
               f"- **Category:** {result['category']}\n"
               f"- **Issue Summary:** {data.summary}") # Summary taken from state data[cite: 2]
    else:
        msg = f"❌ **SAP Integration Error:** {result['message']}"
    
    return {"final_response": msg}

# Build the Agentic Graph[cite: 3]
workflow = StateGraph(AgentState)

workflow.add_node("extractor", extraction_node)
workflow.add_node("sap_creator", sap_execution_node)

workflow.set_entry_point("extractor")

# The routing logic: Only proceed if extracted_data is fully populated[cite: 3]
workflow.add_conditional_edges(
    "extractor",
    lambda x: "proceed" if x.get("extracted_data") else "fail",
    {
        "proceed": "sap_creator", 
        "fail": END  # Returns the clarifying question to the UI[cite: 5]
    }
)

workflow.add_edge("sap_creator", END)

agent_app = workflow.compile()


