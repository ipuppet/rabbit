from abc import abstractmethod

from .http import Request


class IRouter:
    @abstractmethod
    def match(self) -> dict: pass


class Router(IRouter):
    request: Request
    strict_mode: bool
    default_token: str

    def __init__(self, request: Request):
        self.request = request
        self.strict_mode = False
        self.default_token = r'([_0-9a-zA-Z\x{4e00}-\x{9fa5}]*)'

    def match(self) -> dict:
        """TODO match

        Returns:
            匹配结果
        """
        pass
