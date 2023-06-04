import requests
import base64
import json
import settings

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
        self.getWorkspaces()
        self.getClients()

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
        print(self.clients)



