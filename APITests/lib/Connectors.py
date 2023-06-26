class sendRequest:
    def __init__(self, baseUrl, service, action,):
        self.baseUrl = baseUrl
        self.service = service
        self.action = action
        self.url = baseUrl + service + action

class header():
    def __init__(self, auth):
        self.auth = auth


class body():
    def __init__(self, body, ):
        self.body = body
        # self.body1 = body1



