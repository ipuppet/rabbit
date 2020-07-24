from enum import Enum

from rabbit.http.server import Header


class HTTPStatus(Enum):
    HTTP_200 = '200 OK'
    HTTP_201 = '201 Created'
    HTTP_204 = '204 No Content'
    HTTP_400 = '400 Bad Request'
    HTTP_401 = '401 Unauthorized'
    HTTP_403 = '403 Forbidden'
    HTTP_404 = '404 Not Found'
    HTTP_405 = '405 Method Not Allowed'
    HTTP_500 = '500 Internal Server Error'


class Response:
    content: str
    http_status: HTTPStatus
    header: Header
    http_version: str

    def __init__(self):
        self.set('', HTTPStatus.HTTP_200)

    def set(self, content: str, http_status: HTTPStatus = None, header: Header = None, http_version: str = '1.1'):
        self.content = content
        self.http_status = HTTPStatus.HTTP_200 if http_status is None else http_status
        self.header = Header() if header is None else header
        self.http_version = http_version


class JsonResponse(Response):
    def __init__(self):
        super(JsonResponse, self).__init__()
        super().header.set('Content-Type', 'application/json')

    @property
    def json(self) -> str:
        """
        获取json属性的值
        Returns:
            json字符串，就是父类的content属性的值
        """
        return self.content

    @json.setter
    def json(self, json_str: str):
        """设置json属性的值

        json字符串将会保存在父类content属性内

        Args:
            json_str: json字符串
        """
        self.content = json_str
