import os
import requests
from requests.auth import HTTPBasicAuth
import logging
from src.schema import WorkOrderSchema

logger = logging.getLogger(__name__)

class SAPConnector:
    def __init__(self):
        # Default to local mock if environment variables are missing
        self.base_url = os.getenv("SAP_ODATA_URL","http://localhost:8080/sap/opu")
        self.auth = HTTPBasicAuth(os.getenv("SAP_USER", "user"), os.getenv("SAP_PWD", "pass"))

    def create_work_order(self, data: WorkOrderSchema):
        endpoint = f"{self.base_url}/simulator"
        try:
            payload = data.model_dump(by_alias=True)
            response = requests.post(endpoint, json=payload, auth=self.auth, timeout=10)
            response.raise_for_status()
            
            # Extract the full 'd' object to get Status and Category
            sap_data = response.json()["d"]
            print(sap_data)
            return {
                "status": "success", 
                "order_id": sap_data.get("OrderID"),
                "sap_status": sap_data.get("Status"),
                "category": sap_data.get("Category"),
                "summary":data.summary
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
        
