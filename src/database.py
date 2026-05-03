import json
import os,re
from src.schema import WorkOrderSchema

DB_FILE = "work_orders_db.json"

def sanitize_string(text: str) -> str:
    """Removes markdown backticks, extra spaces, and hidden characters."""
    if not text:
        return ""
    # Remove backticks and strip whitespace
    clean_text = text.replace("`", "").strip()
    # Remove any non-printable ASCII if necessary
    return re.sub(r'[^\x20-\x7E]', '', clean_text)

def save_to_json(order_id: str, sap_status: str, data: WorkOrderSchema):
    history = load_all_records()
    # 1. Clean the primary keys
    clean_id = sanitize_string(order_id).upper()  # Force uppercase for WOXXXXX consistency
    entry = data.model_dump(by_alias=True)
    entry["order_id"] = clean_id
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