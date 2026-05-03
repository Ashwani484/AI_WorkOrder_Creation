from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage
from src.schema import WorkOrderSchema
from src.sap_service import SAPConnector
from src.database import save_to_json
from src.llm import init_llm
class AgentState(TypedDict):
    messages: List[BaseMessage]
    extracted_data: Optional[WorkOrderSchema]
    final_response: Optional[str]

llm = init_llm("openAI")
# Configure LLM to force output into your new schema
structured_llm = llm.with_structured_output(WorkOrderSchema)

def extraction_node(state: AgentState):
    """Extracts problem area, severity, and location from chat."""
    try:
        results = structured_llm.invoke(state["messages"])
        return {"extracted_data": results}
    except Exception:
        return {"final_response": "Could not categorize the issue. Please provide Site, Problem, and Severity."}

def sap_execution_node(state: AgentState):
    sap = SAPConnector()
    result = sap.create_work_order(state["extracted_data"])
    summary_WO=state["extracted_data"]
    print(result)
    if result["status"] == "success":
        # Format string to include ID, SAP Status, and Category[cite: 3, 4]
        msg = (f"✅ **Work Order Created Successfully**\n\n"
               f"- **Work Order ID:** {result['order_id']}\n"
               f"- **Processing Status:** {result['sap_status']}\n"
               f"- **Category:** {result['category']}\n"
               f"- **Summary:** {result["summary"]}")
    else:
        msg = f" **SAP Integration Error:** {result['message']}"
    
    return {"final_response": msg}

# Graph definition remains the same as previously defined[cite: 3]
workflow = StateGraph(AgentState)
workflow.add_node("extractor", extraction_node)
workflow.add_node("sap_creator", sap_execution_node)
workflow.set_entry_point("extractor")
workflow.add_conditional_edges("extractor", lambda x: "proceed" if x.get("extracted_data") else "fail", {"proceed": "sap_creator", "fail": END})
workflow.add_edge("sap_creator", END)
agent_app = workflow.compile()
