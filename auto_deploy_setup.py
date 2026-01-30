import os
import subprocess
import sys

def run_command(command, cwd=None):
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(e.stderr)
        return None

def main():
    print("==================================================")
    print("      ComicGenerator GitHub Deployment Setup      ")
    print("==================================================")
    print("\nThis script will help you push your code to GitHub and set up deployment.\n")
    
    print("Step 1: Create a Repository")
    print("---------------------------")
    print("1. Open your browser and go to: https://github.com/new")
    print("2. Enter 'ComicGenerator' as the Repository name.")
    print("3. Choose 'Public' or 'Private' (Private is recommended).")
    print("4. Do NOT check 'Initialize this repository with a README'.")
    print("5. Click 'Create repository'.")
    print("\n")
    
    repo_url = input("Step 2: Enter your Repository URL (e.g., https://github.com/username/ComicGenerator.git): ").strip()
    
    if not repo_url:
        print("Error: Repository URL is required.")
        return

    print("\nStep 3: configuring Git Remote...")
    # Remove existing origin if exists to be safe
    run_command("git remote remove origin")
    
    # Add new origin
    if run_command(f"git remote add origin {repo_url}") is None:
        # If it failed, maybe it wasn't there, or something else. Try to check remote
        print("Could not add remote. Checking status...")
    
    print("Remote configured.")
    
    print("\nStep 4: Pushing code to GitHub...")
    print("Note: A browser window or credential dialog may appear. Please log in.")
    
    # Rename branch to main just in case
    run_command("git branch -M main")
    
    # Push
    try:
        subprocess.check_call("git push -u origin main", shell=True)
        print("\n✅ Code pushed successfully!")
    except subprocess.CalledProcessError:
        print("\n❌ Push failed. Please check your credentials and try running 'git push -u origin main' manually.")
        # Continue anyway to show secrets
        
    print("\nStep 5: Configure GitHub Secrets")
    print("--------------------------------")
    print("Go to: Repository Settings -> Secrets and variables -> Actions -> New repository secret")
    print("Add the following secrets:\n")
    
    print(f"1. SERVER_HOST: 122.51.215.20")
    print(f"2. SERVER_USER: root")
    print(f"3. MIDJOURNEY_API_KEY: <Your Midjourney API Key>")
    
    try:
        with open("deploy_key.pem", "r") as f:
            private_key = f.read()
        print("4. SSH_PRIVATE_KEY:")
        print("--------------------")
        print(private_key)
        print("--------------------")
        print("(Copy the entire block above including BEGIN and END lines)")
    except FileNotFoundError:
        print("Error: deploy_key.pem not found. Please run setup_gh_secrets.py first.")

    print("\nDone! Once you add these secrets, your next push (or manual workflow run) will deploy the app.")

if __name__ == "__main__":
    main()
