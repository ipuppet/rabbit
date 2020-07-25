from src.rabbit import Request


class Router:
    request: Request

    def __init__(self, request: Request):
        self.request = request
