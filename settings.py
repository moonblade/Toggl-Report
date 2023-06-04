import os

base = os.path.dirname(__file__)
apiKeyFile = base + "/secret/togglApiKey"

with open(apiKeyFile) as f:
    apiKey=f.read().strip()
