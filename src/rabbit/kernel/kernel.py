from wsgiref import simple_server

from src.rabbit import RequestCreator
from src.rabbit import Response
from src.rabbit.router import Router


class Kernel:
    port: int

    def __init__(self):
        self.port = 8080

    def application(self, environ, start_response):
        response = self.handle_request(environ)
        start_response(response.http_status, response.header.get_tuple_list())
        return [response.content]

    def handle_request(self, environ) -> Response:
        request = RequestCreator().create_by_environ(environ)
        # TODO 匹配路由
        router = Router(request)
        return

    def run(self):
        httpd = simple_server.make_server('', self.port, self.application)
        print('Serving http on port {}'.format(self.port))
        httpd.serve_forever()
