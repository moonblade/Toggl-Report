import os
import json
from datetime import datetime, timedelta

base = os.path.dirname(__file__)
secret= base + "/secret"
apiKeyFile = secret+ "/togglApiKey"

with open(apiKeyFile) as f:
    apiKey=f.read().strip()

with open(secret + "/workspacename") as f:
    workspacename = f.read().strip()

with open(secret + "/clients.json") as f:
    clients = json.load(f);

if int(datetime.utcnow().strftime("%d")) > 15:
    endDate = datetime.utcnow().strftime("%Y-%m-%d")
    startDate = datetime.utcnow().replace(day=1).strftime("%Y-%m-%d")
    startDatePreviousMonth = (datetime.utcnow().replace(day=1) - timedelta(days=1)).replace(day=1).strftime("%Y-%m-%d")
else:
    endDate = (datetime.utcnow().replace(day=1) - timedelta(days=1)).strftime("%Y-%m-%d")
    startDate = (datetime.utcnow().replace(day=1) - timedelta(days=1)).replace(day=1).strftime("%Y-%m-%d")
    startDatePreviousMonth = (datetime.utcnow().replace(day=1) - timedelta(days=35)).replace(day=1).strftime("%Y-%m-%d")

reportFilePath = base + "/report.json"
