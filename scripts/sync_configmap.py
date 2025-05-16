import os
import subprocess
import yaml
import requests

envs = ['qa', 'uat', 'prod']
dev_file = 'k8s/dev/configmap.yaml'
base_branch = subprocess.getoutput("git rev-parse --abbrev-ref HEAD")

def read_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def write_yaml(path, data):
    with open(path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)

def prompt_llm(dev_yaml, target_yaml, env):
    prompt = f"""
    You are a Kubernetes expert.

    Here is the updated dev ConfigMap:
    ```yaml
    {yaml.dump(dev_yaml)}
    """

