import os
import subprocess
import requests
import yaml

# Config
dev_file = 'k8s/dev/configmap.yaml'
envs = ['qa', 'xuat', 'prod']
base_branch = 'main'

def read_yaml(path):
    print(f"Reading YAML file: {path}")
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
            print(f"Successfully read YAML from {path}")
            return data
    except Exception as e:
        print(f"Failed to read {path}: {e}")
        return None

def write_yaml(path, data):
    print(f"Writing YAML to: {path}")
    try:
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
        print(f"Successfully wrote YAML to {path}")
    except Exception as e:
        print(f"Failed to write to {path}: {e}")

def prompt_llm(dev_yaml, target_yaml, env):
    prompt = f"""
You are a Kubernetes ConfigMap sync assistant.
Given the ConfigMap in dev and the current ConfigMap in {env}, produce the updated ConfigMap YAML for {env} by syncing any changes from dev.
Return only valid YAML.
Current {env} ConfigMap:
{yaml.dump(target_yaml)}
Dev ConfigMap:
{yaml.dump(dev_yaml)}
Updated {env} ConfigMap:
"""

    print(f"Sending prompt to LLM for {env}...")

    try:
        response = requests.post(
            os.environ.get("OLLAMA_HOST") + "/chat",
            json={
                "model": os.environ.get("MODEL", "mistral"),
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"]
        print(f"LLM response for {env}:\n{answer}")
        updated_yaml = yaml.safe_load(answer)
        return updated_yaml
    except Exception as e:
        print(f"LLM request or parsing failed for {env}: {e}")
        return None

def run_git(*args):
    print(f"git {' '.join(args)}")
    result = subprocess.run(["git", *args], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Git command failed: {' '.join(args)}")
        print(f"stderr: {result.stderr}")
        raise Exception(f"Git command failed: {' '.join(args)}")
    return result.stdout.strip()

def create_pr(env):
    branch = f"sync-configmap-{env}"
    print(f"Creating branch {branch}...")

    # Checkout base branch first
    run_git("checkout", base_branch)
    run_git("pull", "origin", base_branch)

    # Create and checkout new branch
    run_git("checkout", "-B", branch)

    # Stage changes
    run_git("add", f"k8s/{env}/configmap.yaml")

    # Check if any changes to commit
    status = run_git("status", "--porcelain")
    if not status:
        print(f"No changes detected for {env}, skipping commit and PR creation.")
        return

    # Commit and push
    run_git("commit", "-m", f"Sync ConfigMap from dev to {env}")
    run_git("push", "-u", "origin", branch)

    # Create PR using GitHub CLI
    print(f"Creating PR for branch {branch}...")
    pr_result = subprocess.run([
        "gh", "pr", "create",
        "--base", base_branch,
        "--head", branch,
        "--title", f"Sync ConfigMap to {env}",
        "--body", f"Automated sync of ConfigMap changes from dev to {env}."
    ], capture_output=True, text=True)

    if pr_result.returncode == 0:
        print(f"PR created for {env}.")
        print(pr_result.stdout)
    else:
        print(f"Failed to create PR for {env}: {pr_result.stderr}")

def main():
    dev_yaml = read_yaml(dev_file)
    if not dev_yaml:
        print("Could not read dev ConfigMap. Exiting.")
        return

    for env in envs:
        target_path = f"k8s/{env}/configmap.yaml"
        target_yaml = read_yaml(target_path) or {}

        updated_yaml = prompt_llm(dev_yaml, target_yaml, env)
        if not updated_yaml:
            print(f"No update returned by LLM for {env}. Skipping.")
            continue

        if updated_yaml != target_yaml:
            print(f"Changes detected for {env}, updating file...")
            write_yaml(target_path, updated_yaml)
            create_pr(env)
        else:
            print(f"No changes needed for {env}.")

if __name__ == "__main__":
    main()

