import os, requests
from dotenv import load_dotenv

load_dotenv()

def get_report_details():
    workspace_id = os.getenv("POWERBI_WORKSPACE_ID")
    report_id = os.getenv("POWERBI_REPORT_ID")

    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}"

    res = requests.get(url, headers=headers)
    res.raise_for_status()
    return res.json()

def get_access_token():
    tenant_id = os.getenv("POWERBI_TENANT_ID")
    client_id = os.getenv("POWERBI_CLIENT_ID")
    client_secret = os.getenv("POWERBI_CLIENT_SECRET")

    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://analysis.windows.net/powerbi/api/.default"
    }

    res = requests.post(url, data=data)
    res.raise_for_status()
    return res.json()["access_token"]


def generate_embed_token():
    workspace_id = os.getenv("POWERBI_WORKSPACE_ID")
    report_id = os.getenv("POWERBI_REPORT_ID")
    dataset_id = os.getenv("POWERBI_DATASET_ID")

    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}/GenerateToken"

    body = {
        "datasets": [{"id": dataset_id}],
        "reports": [{"id": report_id}],
        "targetWorkspaces": [{"id": workspace_id}],
        "accessLevel": "View"
    }

    res = requests.post(url, headers=headers, json=body)
    res.raise_for_status()
    return res.json()


def get_latest_metrics():
    # Example simulated data — later can change to fetch from dataset/table
    return {
        "berth_time": 12.3,
        "carbon_savings": 1600,
        "arrival_accuracy": 96.1
    }