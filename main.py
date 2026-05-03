from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.orchestrator import agent_app
from src.database import save_to_json, find_by_id, load_all_records
from langchain_core.messages import HumanMessage

app = FastAPI(title="Industrial Work Order Agent")

class ChatInput(BaseModel):
    query: str

@app.post("/v1/work-order/create")
async def handle_request(payload: ChatInput):
    # 1. Run the Agentic Orchestrator
    initial_state = {"messages": [HumanMessage(content=payload.query)]}
    output = agent_app.invoke(initial_state)
    
    # 2. Check for Extraction Errors
    if output.get("final_response") and "Could not categorize" in output["final_response"]:
        return {"response": output["final_response"]}

    # 3. Save to JSON if successful
    response_text = output["final_response"]
    if "Work Order ID:" in response_text:
        # Extract ID from the string "Work Order Created Successfully! ID: WO1234"
        order_id = response_text.split("ID:** ")[1].split("\n")[0]
        status = response_text.split("Status:** ")[1].split("\n")[0]
        save_to_json(order_id, status,output["extracted_data"])
        
    return {"response": response_text}

@app.get("/v1/work-order/history")
async def get_history():
    return load_all_records()

@app.get("/v1/work-order/{order_id}")
async def get_details(order_id: str):
    record = find_by_id(order_id)
    if not record:
        raise HTTPException(status_code=404, detail="Work order not found in history.")
    return record



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)