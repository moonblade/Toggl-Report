import requests
import base64
import json
import settings
import csv
from datetime import timedelta
from pprint import pprint
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Toggle')
    parser.add_argument('-p', '--previous_month', action='store_true', help='Use the previous month')
    return parser.parse_args()

class Toggl():
    def __init__(self, apiKey):
        self.apiKey = apiKey
        self.args = parse_args()
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

    def convert_to_inr(self, amount, currency):
        response = requests.get(f"https://api.exchangerate-api.com/v4/latest/INR")
        data = response.json()
        if response.status_code == 200 and 'rates' in data:
            rates = data['rates']
            if currency in rates:
                conversion_rate = rates[currency]
                inr_amount = amount / conversion_rate
                return inr_amount
        return 0

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
            startDate = settings.startDate
            if self.args.previous_month:
                startDate = settings.startDatePreviousMonth
            data = {
                "client_ids":[self.clients[client["clientName"]]],
                "duration_format":"classic",
                "end_date":settings.endDate,
                "hour_format":"string",
                "start_date":startDate,
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
                "startDate": startDate,
                "endDate": settings.endDate,
                "totalHours": totalHours,
                "billableHours": billableHours,
                "amount": round(totalAmount, 2),
                "amountInr": round(self.convert_to_inr(totalAmount, client["currencyCode"])),
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
