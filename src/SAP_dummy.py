from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
import random
import uuid
from schema import WorkOrderSchema
app = FastAPI(title="Simulator SAP S/4HANA OData Service")

#SAP application simulator

@app.get("/sap_simulator/")
async def get_metadata():
    """Simulates the metadata/CSRF token fetch endpoint."""
    return {"message": "SAP OData Service Active", "csrf_token": str(uuid.uuid4())}

@app.post("/sap/opu/simulator")
async def create_work_order(data: WorkOrderSchema):
    print(f"DEBUG: Processing {data.intent} for {data.problem_area} at {data.location_id}")
    return {
        "d": {
            "OrderID": f"WO{random.randint(1000, 9999)}",
            "Status": "Received",
            "Category": data.problem_area
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

    