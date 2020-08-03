import re
from enum import Enum
from urllib.parse import quote, parse_qs


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


class Header:
    headers: dict
    cache_control: dict

    def __init__(self, headers=None):
        if headers is None:
            headers = {}
        self.add(headers)

    @staticmethod
    def __parse_key(key):
        """格式化header字段

        用来格式化header的字段，防止发生错误

        Args:
            key: 待处理的字段

        Returns:
            处理后的字段
        """
        return key.lower().replace('_', '-')

    def __str__(self):
        return self.to_string()

    def to_string(self):
        """将header转换为字符串

        Returns:
            转换后内容
        """

        def capitalize(s: str) -> str:
            return s.capitalize()

        content = ''
        for name in self.headers:
            for value in self.headers[name]:
                name = '-'.join(map(capitalize, name.split('-')))
                if isinstance(value, list):
                    value = ', '.join(value)
                content += '{}: {}\r\n'.format(name, value)
        return content

    def __getitem__(self, key):
        return self.get(key)

    def get(self, key, default=None, first=False):
        """从header中取值

        找不到需要的值时将返回传入的默认值
        可能找到多个值，可以规定是否只返回找到的第一个值

        Args:
            key: 要取的值
            default: 默认值
            first: 是否只取第一个值

        Returns:
            找到的值或者提供的默认值
        """
        key = self.__parse_key(key)
        headers = self.headers
        if not self.has(key):
            if default is None:
                return None if first else []
            return default if first else [default]
        if first:
            if isinstance(headers[key], list):
                if len(headers[key]) > 0:
                    return str(headers[key][0])
                else:
                    return default
            else:
                return str(headers[key])
        return headers.get(key, [default])

    def all(self) -> dict:
        """获取 header 所有字段

        Returns:
            header 所有字段
        """
        return self.headers

    def get_tuple_list(self):
        headers = []
        for k, v in self.headers:
            headers.append((k, v))
        return headers

    def add(self, headers: dict):
        """向header中添加字段

        该方法不会替换原有字段，而是直接增加

        Args:
            headers: 需要添加的字段

        Returns:
            self
        """
        for key in headers:
            self.set(key, headers[key], False)
        return self

    def __setitem__(self, key, value):
        self.set(key, value)

    def set(self, key, values, replace=True):
        """设置字段的值

        可以选择替换原来的字段或者保留原来的字段并且添加新字段

        Args:
            key: 字段
            values: 值
            replace: 是否替换

        Returns:
            self
        """
        key = self.__parse_key(key)
        if not self.has(key):
            self.headers[key] = []
        if replace:
            if isinstance(values, list):
                self.headers[key] = values
            else:
                self.headers[key] = [values]
        else:
            self.headers[key].append(values)
        if 'cache-control' == key:
            self.cache_control = self._parse_cache_control(', '.join(self.headers[key]))
        return self

    def has(self, key) -> bool:
        """查询header中是否有该字段

        Args:
            key: 需要查询的字段

        Returns:
            True or False
        """
        return self.__parse_key(key) in self.headers

    def is_empty(self):
        """header是否为空

        Returns:
            True or False
        """
        if self.headers:
            return True
        return False

    def remove(self, key):
        """移除某个字段

        Args:
            key: 字段
        """
        key = self.__parse_key(key)
        del self.headers[key]
        if 'cache-control' == key:
            self.cache_control = {}

    def add_cache_control_directive(self, key, value=True):
        """缓存控制字段

        直接设置Cache-Control

        Args:
            key: 属性
            value: True or False
        """
        self.cache_control[key] = value
        self.set('Cache-Control', self._get_cache_control_header())

    def has_cache_control_directive(self, key):
        return key in self.cache_control

    def get_cache_control_directive(self, key):
        return self.cache_control[key] if key in self.cache_control else None

    def remove_cache_control_directive(self, key):
        del self.cache_control[key]
        self.set('Cache-Control', self._get_cache_control_header())

    def _get_cache_control_header(self):
        parts = []
        for key, value in zip(self.cache_control.keys(), self.cache_control.values()):
            if value:
                parts.append(key)
            else:
                if re.search(r'#[^a-zA-Z0-9._-]#', value):
                    value = '"' + value + '"'
                parts.append("{}={}".format(key, value))
        return ', '.join(parts)

    @staticmethod
    def _parse_cache_control(header):
        cache_control = {}
        matches = re.findall(r'#([a-zA-Z][a-zA-Z_-]*)\s*(?:=(?:"([^"]*)"|([^ \t",]*)))?#', header)
        for match in matches:
            cache_control[match[0].lower()] = match[2] if match[2] else (match[1] if match[1] else True)
        return cache_control


class Request:
    """
    HTTP请求
    """
    attributes: dict
    query: dict
    cookie: dict
    header: Header

    environ: dict
    url_scheme: str
    request_method: str
    script_name: str
    path_info: str
    server_name: str
    server_port: str

    def __init__(self):
        """
        初始化数据
        """
        self.cookie = {}
        self.header = Header()

        self.path_info = ''
        self.server_name = ''
        self.request_method = 'GET'

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

    def get_url(self):
        url = self.environ['wsgi.url_scheme'] + '://'

        if self.environ.get('HTTP_HOST'):
            url += self.environ['HTTP_HOST']
        else:
            url += self.environ['SERVER_NAME']

            if self.environ['wsgi.url_scheme'] == 'https':
                if self.environ['SERVER_PORT'] != '443':
                    url += ':' + self.environ['SERVER_PORT']
            else:
                if self.environ['SERVER_PORT'] != '80':
                    url += ':' + self.environ['SERVER_PORT']

        url += quote(self.environ.get('SCRIPT_NAME', ''))
        url += quote(self.environ.get('PATH_INFO', ''))
        if self.environ.get('QUERY_STRING'):
            url += '?' + self.environ['QUERY_STRING']
        return url

    @staticmethod
    def create_by_environ(environ):
        """
        通过environ创建一个Request类并返回
        Args:
            environ:

        Returns:
            Request()
        """
        request = Request()
        request.url_scheme = environ['wsgi.url_scheme']
        request.request_method = environ['REQUEST_METHOD']
        request.script_name = environ['SCRIPT_NAME']
        request.path_info = environ['PATH_INFO']
        request.server_name = environ['SERVER_NAME']
        request.server_port = environ['SERVER_PORT']
        if environ.get('QUERY_STRING'):
            request.query = parse_qs(environ['QUERY_STRING'])
        header = Header({
            'Content-Type': environ['CONTENT_TYPE'],
            'Content-Length': environ['CONTENT_LENGTH'],
        })
        headers = {}
        for key, value in environ.items():
            if key[0:4] == 'HTTP_':
                headers[key] = value
        request.header = header.add(headers)
        return request


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
