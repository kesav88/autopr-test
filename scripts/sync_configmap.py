import os
import subprocess
import requests
import yaml

dev_file = 'k8s/dev/configmap.yaml'
envs = ['qa', 'uat', 'prod']
base_branch = 'main'

def read_yaml(path):
    print(f"📖 Reading YAML file: {path}")
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Failed to read {path}: {e}")
        return None

def write_yaml(path, data):
    print(f"💾 Writing YAML to: {path}")
    try:
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
    except Exception as e:
        print(f"❌ Failed to write to {path}: {e}")

def prompt_llm(dev_yaml, target_yaml, env):
    prompt = f"""
    Here is the current ConfigMap for {env}:

    ```yaml
    {yaml.dump(target_yaml)}
    """

