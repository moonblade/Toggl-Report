import os

base = os.path.dirname(__file__)
secret= base + "/secret"
apiKeyFile = secret+ "/togglApiKey"

with open(apiKeyFile) as f:
    apiKey=f.read().strip()

with open(secret + "/workspacename") as f:
    workspacename = f.read().strip()
