import re


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
        """
        for key in headers:
            self.set(key, headers[key], False)

    def __setitem__(self, key, value):
        self.set(key, value)

    def set(self, key, values, replace=True):
        """设置字段的值

        可以选择替换原来的字段或者保留原来的字段并且添加新字段

        Args:
            key: 字段
            values: 值
            replace: 是否替换
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


class Server:
    pass
