import requests
import base64
import json
import settings
import csv
from datetime import timedelta
from pprint import pprint

class Toggl():
    def __init__(self, apiKey):
        self.apiKey = apiKey
        self.setup()

    def setup(self):
        self.headers = {
            'content-type': 'application/json',
            'Authorization': 'Basic ' + base64.b64encode((self.apiKey + ":api_token").encode("utf-8")).decode("utf-8")
        }
        self.baseUrl = "https://api.track.toggl.com/api"
        self.reportsBaseUrl = "https://api.track.toggl.com/reports/api"
        self.timeEntries = {}
        self.getWorkspaces()
        self.getClients()
        self.getReportsForClients()
        self.makeReportJson()

    def getWorkspaces(self):
        response = requests.get(self.baseUrl + '/v9/workspaces', headers=self.headers)
        for workspace in response.json():
            if workspace["name"] == settings.workspacename:
                self.workspaceId = workspace["id"]
                return

    def getClients(self):
        response = requests.get(self.baseUrl + "/v9/workspaces/"+str(self.workspaceId)+"/clients", headers=self.headers)
        self.clients = {}
        for client in response.json():
            self.clients[client["name"].lower().replace(" ","")] = client["id"]

    def getReportsForClients(self):
        for client in settings.clients:
            data = {
                "client_ids":[self.clients[client["clientName"]]],
                "duration_format":"classic",
                "end_date":settings.endDate,
                "hour_format":"string",
                "start_date":settings.startDate,
            }
            response = requests.post(self.reportsBaseUrl + '/v3/workspace/'+str(self.workspaceId)+'/search/time_entries.csv', json=data, headers=self.headers)
            reader = csv.DictReader(response.text.splitlines())
            timeEntries = []
            totalHours = timedelta()
            billableHours = timedelta()
            totalAmount = 0
            for row in reader:
                row["billable"] = ":ignore:" not in row["Description"]
                duration = [int(x) for x in row["Duration"].split(":")]
                delta = timedelta(hours=duration[0], minutes=duration[1], seconds=duration[2])
                project=row["Project"].lower()
                ratePerHour = int(client["ratePerHour"])
                if "projects" in client:
                    for clientProject in client["projects"]:
                        if clientProject["name"] in project or project in clientProject["name"]:
                            if "ratePerHour" in clientProject:
                                ratePerHour = int(clientProject["ratePerHour"])
                amount = round(delta.total_seconds() * ratePerHour / 3600, 2)
                row["amount"] = amount if row["billable"] else 0
                row["ratePerHour"] = ratePerHour
                totalHours += delta
                if row["billable"]:
                    billableHours += delta
                    totalAmount += row["amount"]
                del row['ï»¿User']
                timeEntries.append(row)
            self.timeEntries[client["clientName"]] = {
                "timeEntries": timeEntries,
                "startDate": settings.startDate,
                "endDate": settings.endDate,
                "totalHours": totalHours,
                "billableHours": billableHours,
                "amount": totalAmount,
                "currency": client["currency"],
                "clientName": client["clientName"],
                "ratePerHour": client["ratePerHour"],
                "displayName": client["displayName"]
            }

    def makeReportJson(self):
        with open(settings.reportFilePath, "w") as f:
            json.dump(self.timeEntries, f, default=str)


if __name__ == "__main__":
    t = Toggl(settings.apiKey)
    print(json.dumps(t.timeEntries))
