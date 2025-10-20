import os, requests
from dotenv import load_dotenv
import time

load_dotenv()

WORKSPACE_ID = os.getenv("POWERBI_WORKSPACE_ID")
REPORT_ID = os.getenv("POWERBI_REPORT_ID")
TENANT_ID = os.getenv("POWERBI_TENANT_ID")
CLIENT_ID = os.getenv("POWERBI_CLIENT_ID")
CLIENT_SECRET = os.getenv("POWERBI_CLIENT_SECRET")
DATASET_ID = os.getenv("POWERBI_DATASET_ID")

def get_report_details():
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/reports/{REPORT_ID}"

    res = requests.get(url, headers=headers)
    res.raise_for_status()
    return res.json()

def get_access_token():
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://analysis.windows.net/powerbi/api/.default"
    }

    res = requests.post(url, data=data)
    res.raise_for_status()
    return res.json()["access_token"]


def generate_embed_token():
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/reports/{REPORT_ID}/GenerateToken"

    body = {
        "datasets": [{"id": DATASET_ID}],
        "reports": [{"id": REPORT_ID}],
        "targetWorkspaces": [{"id": WORKSPACE_ID}],
        "accessLevel": "View"
    }

    res = requests.post(url, headers=headers, json=body)
    res.raise_for_status()
    return res.json()


def get_filtered_data(filters):
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}

    base_url = f"https://app.powerbi.com/groups/{WORKSPACE_ID}/reports/{REPORT_ID}"

    if filters:
        filter_str = "&".join([f"filter={filter}" for filter in filters])
        url = f"{base_url}?{filter_str}"
    else:
        url = base_url

    res = requests.get(url, headers=headers)
    res.raise_for_status()
    return res.json()

def get_data_from_dataset_with_query(query):
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/datasets/{DATASET_ID}/executeQueries"

    body = {
        "queries": [
            {
                "query": query  # DAX or query string
            }
        ]
    }
    res = requests.post(url, headers=headers, json=body)
    res.raise_for_status()
    
    return res.json()

#def get_datasets():
#    token = get_access_token()
#    headers = {"Authorization": f"Bearer {token}"}
#
#    url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/datasets"
#    
#    res = requests.get(url, headers=headers)
#    res.raise_for_status()
#
#    datasets = res.json()
#    return datasets

def get_latest_metrics():
    return {
        "berth_time": 12.3,
        "carbon_savings": 1600,
        "arrival_accuracy": 96.1
    }

def export_report_to_file():
    access_token = get_access_token()
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/reports/{REPORT_ID}/ExportTo"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    body = {
        "format": "PDF"
    }

    res = requests.post(url, headers=headers, json=body)
    res.raise_for_status()
    
    export_id = res.json().get('id')
    print(f"Export initiated with ID: {export_id}")
    return export_id

def download_exported_file(export_id):
    access_token = get_access_token()
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/reports/{REPORT_ID}/ExportTo/{export_id}/file"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()

        with open("exported_report.pdf", "wb") as f:
            f.write(res.content)

        print("File downloaded successfully.")

    except requests.exceptions.HTTPError as err:
        print(f"Error downloading the file: {err}")

def check_export_status(export_id):
    access_token = get_access_token()
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/reports/{REPORT_ID}/ExportTo/{export_id}"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        
        status_data = res.json()
        # Check if export is ready
        if status_data.get("status") == "Succeeded":
            print("Export completed successfully.")
            return True
        else:
            print("Export still processing, retrying...")
            return False

    except requests.exceptions.HTTPError as err:
        print(f"Error checking export status: {err}")
        return False