from typing import Awaitable, Optional
import tornado.web
import tornado.ioloop
import traceback

from app.utils.constants import Key
from app.utils.authentication import JwtToken
from app.utils.common import render_error_page, get_cas_login_url, refresh_all_cookies


class LoginSuccessHandler(tornado.web.RequestHandler):

    def options(self):
        print("The requet is arrived here")
        
        try:

            request_host = self.request.host
            cookie_key = str(request_host+"_user_authentication_data").replace(".","_").replace(":","_")

            print(cookie_key)

            # Check if the user_data cookie exists
            session = self.get_secure_cookie(cookie_key)
            print(session)

            # if session:
            #     # Continue with the original handler function
            #     pass
            # else:
            #     redirect_to_cas_login_page(self)
            #     return

        except Exception as e:
            traceback.print_exc(e)
            render_error_page(
                self, message="Please try logging in again.",
                redirect_url=get_cas_login_url(self), redirect_text="Login Again"
                )


    def prepare(self) -> Awaitable[None] | None:

        return super().prepare()
    
    def get(self):
        host_url = self.get_argument(Key.HOST_URL, "/")
        payload = self.request.payload
        print(f"Login successful for user[{Key.USER_ID}:{payload[Key.USER_ID]}, {Key.FULLNAME}:{payload[Key.FULLNAME]}]")
        self.redirect(host_url)