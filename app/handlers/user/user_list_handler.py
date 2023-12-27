from typing import Awaitable, Optional
import tornado.web
import tornado.ioloop

from app.interceptors import Interceptors

from app.utils.constants import Template

class UserListHandler(tornado.web.RequestHandler):

    @Interceptors.session_interceptor
    def get(self):
        print("User List ...")     
        self.write("User List ...")