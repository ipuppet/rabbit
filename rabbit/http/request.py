import cgi
from enum import Enum

from rabbit.http.server import Header, Server
from rabbit.logger.logger import Logger


def _to_unicode(string, encoding='utf-8'):
    """转换字符编码

    Args:
        string: 待转换字符串
        encoding: 编码

    Returns:
        转换后内容
    """
    return string.decode(encoding)


class MultipartFile:
    """
    文件类
    """

    def __init__(self, storage):
        self.filename = _to_unicode(storage.filename)
        self.file = storage.file


class Method(Enum):
    """
    HTTP请求方法
    """
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    OPTIONS = 'OPTIONS'


class Request:
    """
    HTTP请求
    """
    attributes: dict
    cookie: dict
    server: Server
    header: Header

    request_uri: str
    base_url: str
    path_info: str
    base_path: str
    method: Method

    logger: Logger

    def __init__(self):
        """
        初始化数据
        """
        self.attributes = self.__parse_attributes()
        self.cookie = {}
        self.server = Server()
        self.header = Header()

        self.request_uri = ''
        self.base_url = ''
        self.path_info = ''
        self.base_path = ''
        self.method = Method.GET

    def __getitem__(self, key):
        return self.get(key)

    def get(self, key, default=None):
        """取值

        获取请求中的值，可提供默认值

        Args:
            key: 键
            default: 默认值

        Returns:
            找到的值或提供的默认值
        """
        return self.attributes.get(key, default)

    def has(self, key):
        return key in self.attributes

    @staticmethod
    def __parse_attributes() -> dict:
        """处理参数

        Returns:
            处理后的内容
        """

        def _convert(item):
            if isinstance(item, list):
                return [_to_unicode(i.value) for i in item]
            if item.filename:
                return MultipartFile(item)
            return _to_unicode(item.value)

        fs = cgi.FieldStorage()
        attributes = {}
        for key in fs:
            attributes[key] = _convert(fs.getvalue(key))
        return attributes


class RequestCreator:
    @staticmethod
    def create_by_environ(environ) -> Request:
        request = Request()
        request.path_info = environ['PATH_INFO']
        return request
