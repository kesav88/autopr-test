# ON UBUNTU 22.04 Machine
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl python3 python3-pip python3-venv unzip build-essential gh

#Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

#Start Ollama in the background
ollama pull mistral
ollama serve 

#Check it's running:
curl http://localhost:11434

#Create a Python Virtual Environment
cd ~
python3 -m venv env
source env/bin/activate
pip install pyyaml requests


#Install gh and authenticate with your GitHub account:
gh auth login

#Set Up GitHub Self-Hosted Runner on EC2
#From your GitHub repository, go to:

Settings → Actions → Runners → Add Runner


