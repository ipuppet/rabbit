from wsgiref import simple_server

from .exceptions import ServerRequestError
from .http import Response, Request


class Kernel:
    request: Request

    def __init__(self, request: Request):
        self.request = request

    def response(self) -> Response:
        return Response()


class WSGIApplication:
    def __call__(self, environ, start_response):
        request = Request.create_by_environ(environ)
        kernel = Kernel(request)
        response = kernel.response()
        start_response(response.http_status, response.header.get_tuple_list())
        yield response.content


class Server:
    port: int
    request: Request
    application: WSGIApplication

    def __init__(self, request: Request):
        self.port = 8080
        self.request = request

    def run(self, response: Response):
        if self.request is None:
            raise ServerRequestError('Request is None.')
        self.application = WSGIApplication()
        self.application.response = response
        with simple_server.make_server('', self.port, self.application) as httpd:
            print('Serving on port {}'.format(self.port))
            httpd.serve_forever()
