import requests
import json
import itertools
import os
from time import sleep
import sys

# Constants
GITHUB_REPO = "iabdrahim/WindowsRdp"
GITHUB_API_BASE_URL = f"https://api.github.com/repos/{GITHUB_REPO}"
GITHUB_WORKFLOW_ID = "100349647"
NGROK_API_URL = "https://api.ngrok.com/endpoints"
GITHUB_TOKEN ="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"
NGROK_TOKEN = "2hBMITCvIS8fX4EPpfCDljXmoJW_7AhFvY2BnWKZSiTFAnALt"

def check_is_running():
    url = f"{GITHUB_API_BASE_URL}/actions/runs"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching workflow runs: {response.status_code}")
            print(response.json())
            sys.exit(1)

        runs = response.json().get("workflow_runs", [])
        if runs:
            latest_run = runs[0]
            status = latest_run['status']
            return status == "in_progress"
        else:
            print("No workflow runs found.")
            return False
    except Exception as e:
        print(f"Error happend: {e}")

def get_endpoint():
    headers = {
        "Authorization": f"Bearer {NGROK_TOKEN}",
        "Ngrok-Version": "2"
    }
    response = requests.get(NGROK_API_URL, headers=headers)
    if response.status_code == 200:
        endpoints = response.json().get("endpoints", [])
        if not endpoints:
            print("No endpoint found.")
            sys.exit(1)
        return endpoints[0]["hostport"]
    else:
        print(f"Error fetching endpoint: {response.status_code}")
        print(response.text)
        sys.exit(1)

def rerun_workflow():
    if not check_is_running():
        print("\nRunning...")
        url = f"{GITHUB_API_BASE_URL}/actions/workflows/{GITHUB_WORKFLOW_ID}/dispatches"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {GITHUB_TOKEN}"
        }
        data = {"ref": "main"}
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 204:
            print("Workflow triggered successfully.")
        else:
            print(f"Failed to trigger workflow: {response.status_code}")
            print(response.json())
        sleep(10)
def app():
    rerun_workflow()
    endpoint = get_endpoint()
    print("\nHOST: " + endpoint)
    print("USER: admin")
    print("Password: P@ssw0rd!")

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "check":
            if check_is_running():
                print("Workflow is running!")
            else:
                print("Workflow is not running!")

        elif command == "info":
            endpoint = get_endpoint()
            print("\nHOST: " + endpoint)
            print("USER: admin")
            print("Password: P@ssw0rd!")

        elif command == "run":
            spinner = itertools.cycle(['-', '/', '|', '\\'])
            try:
                while True:
                    print(f"\rChecking if workflow has stopped... {next(spinner)}", end="", flush=True)
                    if not check_is_running():
                        try:
                            app()
                        except Exception as e:
                            print(f"Error happened: {e} (retrying...)")
                    sleep(0.2)
            except KeyboardInterrupt:
                print("\nExiting...")
        else:
            print("Unknown command!")
    else:
        print("Nothing to do!")

if __name__ == "__main__":
    main()
