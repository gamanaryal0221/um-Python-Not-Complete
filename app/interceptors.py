import tornado.web
import tornado.ioloop

import traceback

from app.utils.constants import Config
from app.utils.common import render_error_page

from app.utils.custom_exceptions import NotFoundInApplicationException

# from app.utils.db_utils import get_connection


class Interceptors(tornado.web.RequestHandler):

    @staticmethod
    def session_interceptor(func):
        def wrapper(self, *args, **kwargs):

            try:

                request_host = self.request.host
                cookie_key = request_host + "_user_authentication_data"

                print(cookie_key)

                # Check if the user_data cookie exists
                session = self.get_secure_cookie(cookie_key)
                print(session)

                if session:
                    # Continue with the original handler function
                    return func(self, *args, **kwargs)
                else:
                    redirect_to_cas_login_page(self)
                    return
                
            except Exception as e:
                traceback.print_exception(e)
                render_error_page(self, self.request.full_url(), "Try Again")

        return wrapper
    

def redirect_to_cas_login_page(_self):
    cas_login_url = _self.application.config[Config.CAS_LOGIN_URL]
    if (cas_login_url):

        host_url = _self.request.full_url()
        cas_login_url = cas_login_url.replace("HOST_URL",host_url).rstrip("/")
        print(f"Redirecting to CAS login page\n - host_url:{host_url}\n - cas_login_url:{cas_login_url}")

        _self.redirect(cas_login_url)

    else:
        raise NotFoundInApplicationException("CAS login url not found in application")
    