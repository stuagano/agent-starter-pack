#!/usr/bin/env python3
"""
Penny Assistant Startup Script

Guides the user through Google Cloud project setup, API enablement, service account creation, and prerequisite validation for deploying Penny.
"""
import subprocess
import sys
import os
import json

REQUIRED_APIS = [
    'aiplatform.googleapis.com',      # Vertex AI
    'firestore.googleapis.com',       # Firestore
    'run.googleapis.com',             # Cloud Run
    'iam.googleapis.com',             # IAM
    'cloudbuild.googleapis.com',      # Cloud Build
    # 'calendar.googleapis.com',      # Google Calendar (optional, not enabled by default)
]

SERVICE_ACCOUNT_NAME = 'penny-assistant-sa'
SERVICE_ACCOUNT_DISPLAY = 'Penny Assistant Service Account'


def run_cmd(cmd, check=True, capture_output=False):
    """Run a shell command and return output or raise error."""
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=capture_output, text=True)
        return result.stdout if capture_output else None
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}\n{e}")
        sys.exit(1)

def prompt(msg):
    return input(f"{msg} [y/N]: ").strip().lower() == 'y'

def select_project():
    print("\nChecking current gcloud project...")
    project = run_cmd('gcloud config get-value project', capture_output=True).strip()
    print(f"Current project: {project}")
    if not project or not prompt("Use this project?"):
        run_cmd('gcloud projects list')
        project = input("Enter your Google Cloud project ID: ").strip()
        run_cmd(f'gcloud config set project {project}')
    print(f"Using project: {project}")
    return project

def enable_apis(project):
    print("\nEnabling required Google Cloud APIs...")
    for api in REQUIRED_APIS:
        print(f"Enabling {api}...")
        run_cmd(f'gcloud services enable {api} --project {project}')
    print("All required APIs are enabled.")

def create_service_account(project):
    print("\nChecking for Penny service account...")
    sa_email = f"{SERVICE_ACCOUNT_NAME}@{project}.iam.gserviceaccount.com"
    result = run_cmd(f'gcloud iam service-accounts list --filter="email:{sa_email}" --format="value(email)"', capture_output=True)
    if not result.strip():
        print("Creating service account...")
        run_cmd(f'gcloud iam service-accounts create {SERVICE_ACCOUNT_NAME} --display-name "{SERVICE_ACCOUNT_DISPLAY}" --project {project}')
    else:
        print("Service account already exists.")
    print(f"Service account: {sa_email}")
    return sa_email

def assign_roles(sa_email, project):
    print("\nAssigning roles to service account...")
    roles = [
        'roles/aiplatform.user',
        'roles/datastore.user',
        'roles/run.admin',
        'roles/iam.serviceAccountUser',
        'roles/cloudbuild.builds.editor',
        # 'roles/calendar.readonly',  # Google Calendar (optional, not enabled by default)
    ]
    for role in roles:
        print(f"Assigning {role}...")
        run_cmd(f'gcloud projects add-iam-policy-binding {project} --member="serviceAccount:{sa_email}" --role="{role}"')
    print("All roles assigned.")

def create_service_account_key(sa_email):
    print("\nCreating service account key (JSON)...")
    key_file = f"{SERVICE_ACCOUNT_NAME}-key.json"
    if os.path.exists(key_file):
        print(f"Key file {key_file} already exists. Delete it if you want to regenerate.")
    else:
        run_cmd(f'gcloud iam service-accounts keys create {key_file} --iam-account {sa_email}')
        print(f"Key saved to {key_file}. Keep it secure!")
    return key_file

def setup_github_cloudbuild(project):
    print("\n=== GitHub & Cloud Build Integration ===")
    print("This step will help you connect your GitHub repo to Google Cloud Build for CI/CD.")
    repo_url = input("Enter your GitHub repository URL (e.g., https://github.com/youruser/yourrepo): ").strip()
    if not repo_url.startswith("https://github.com/"):
        print("Invalid GitHub URL. Exiting.")
        sys.exit(1)
    # Extract owner and repo
    try:
        _, _, gh_host, owner, repo = repo_url.split('/', 4)
        repo = repo.split('/')[0] if '/' in repo else repo
    except Exception:
        print("Could not parse GitHub repo URL. Exiting.")
        sys.exit(1)
    print(f"GitHub repo: {owner}/{repo}")
    # Check if GitHub App is installed
    print("Checking for Cloud Build GitHub App installation...")
    print("If not already installed, visit: https://console.cloud.google.com/cloud-build/triggers/connect?project=" + project)
    print("Follow the instructions to install the Google Cloud Build GitHub App on your repo.")
    if not prompt("Continue after installing the GitHub App?"):
        print("Exiting.")
        sys.exit(0)
    # Create trigger
    trigger_name = f"penny-cicd-trigger"
    print(f"Creating Cloud Build trigger '{trigger_name}' for branch 'main'...")
    # Check if trigger already exists
    triggers = run_cmd(f"gcloud beta builds triggers list --project {project} --format=json", capture_output=True)
    triggers = json.loads(triggers)
    for t in triggers:
        if t.get('name', '').endswith(trigger_name):
            print(f"Trigger '{trigger_name}' already exists.")
            return
    # Create the trigger
    create_cmd = (
        f"gcloud beta builds triggers create github "
        f"--name={trigger_name} "
        f"--repo-owner={owner} --repo-name={repo} "
        f"--branch-pattern=^main$ "
        f"--build-config=cloudbuild.yaml "
        f"--project={project}"
    )
    run_cmd(create_cmd)
    print(f"Cloud Build trigger '{trigger_name}' created for {owner}/{repo} (branch: main).\n")
    print("Pushes to 'main' will now trigger Cloud Build CI/CD.")

def main():
    print("""
============================
 Penny Assistant Setup Script
============================
This script will help you:
- Select or create a Google Cloud project
- Enable required APIs (Vertex AI, Firestore, Cloud Run, Cloud Build)
- Create a service account and key
- Assign necessary roles
- Validate your environment
- Set up GitHub/Cloud Build CI/CD integration

Note: Google Calendar integration is optional and not included in the default setup. You can enable it and add permissions later if needed.
""")
    if not prompt("Continue with setup?"):
        print("Exiting.")
        sys.exit(0)
    project = select_project()
    enable_apis(project)
    sa_email = create_service_account(project)
    assign_roles(sa_email, project)
    key_file = create_service_account_key(sa_email)
    setup_github_cloudbuild(project)
    print("\nSetup complete! Next steps:")
    print(f"- Set GOOGLE_APPLICATION_CREDENTIALS={os.path.abspath(key_file)}")
    print("- Deploy Penny backend and Streamlit app using Cloud Run.")
    print("- Configure CI/CD with Cloud Build and GitHub Actions.")
    print("- See technical_requirements.md for full details.")

if __name__ == "__main__":
    main() 