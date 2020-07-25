from abc import abstractmethod

from .http import Request


class IRouter:
    @abstractmethod
    def match(self): pass


class Router(IRouter):
    __request: Request

    @property
    def request(self):
        return self.__request

    @request.setter
    def request(self, request: Request):
        self.__request = request

    def match(self):
        """TODO match

        Returns:

        """
        pass
