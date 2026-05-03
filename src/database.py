import json
import os
from src.schema import WorkOrderSchema

DB_FILE = "work_orders_db.json"

def save_to_json(order_id: str, sap_status: str, data: WorkOrderSchema):
    history = load_all_records()
    entry = data.model_dump(by_alias=True)
    entry["order_id"] = order_id
    entry["sap_status"] = sap_status  # Save the processing status[cite: 4, 5]
    history.append(entry)
    
    with open(DB_FILE, "w") as f:
        json.dump(history, f, indent=4)

def load_all_records():
    """Retrieves all previous work orders."""
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def find_by_id(order_id: str):
    """Retrieves a specific historical record by its ID."""
    history = load_all_records()
    return next((item for item in history if item["order_id"] == order_id), None)