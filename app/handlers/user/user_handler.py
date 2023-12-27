from typing import Awaitable, Optional
import tornado.web
import tornado.ioloop

from app.utils.authentication import JwtToken

from app.utils.constants import Action, Key
from app.utils.common import refresh_all_cookies, get_cookie, render_url_not_found, render_error_page, redirect_to_cas_login_page


class UserActionsHandler(tornado.web.RequestHandler):
    GetActions = [Action.LIST,Action.PROFILE]
    PostActions = [Action.LOGOUT]

    def prepare(self) -> Awaitable[None] | None:
        action = self.path_kwargs.get('action')
        print(f"\nUser [method:{self.request.method},action:{action}]")

        if action != Action.LOGOUT:
            self.request.payLoad = JwtToken.validate(self)
        return super().prepare()

    
    def get(self, action):

        if action in self.GetActions:
            method_to_call = getattr(self, f"get_{action}", None)
            if method_to_call:
                method_to_call()
            else:
                render_url_not_found(self)
        else:
            render_url_not_found(self)


    def post(self, action):
        if action in self.PostActions:
            method_to_call = getattr(self, f"do_{action}", None)
            if method_to_call:
                method_to_call()
            else:
                render_url_not_found(self)
        else:
            render_url_not_found(self)



    def get_list(self):
        # Your 'list' action logic here
        self.write("List of users")

    def get_profile(self):
        # Your 'profile' action logic here
        self.write("View user profile")


    
    def do_logout(self):
        user = f"user[id:{get_cookie(self, Key.USER_ID)}, email:{get_cookie(self, Key.USERNAME)}]"
        print(f"\nLogging out {user}")

        token = get_cookie(self, Key.TOKEN)
        print(f"Token(before):{token}")
        if token:

            if refresh_all_cookies(self, None):
                print(f"Logout successful for {user}")
                self.redirect("/")
            else:
                render_error_page(self)
        
        else:
            render_error_page(self)


        