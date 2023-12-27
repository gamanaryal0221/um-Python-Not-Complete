import tornado.web

from .configurations import Configurations

from app.utils.constants import Key, Environment
from app.utils.common import fetch_data

from app import settings


# for url mappings
import re

from app.interceptors import Interceptors

from app.handlers.login_success import LoginSuccessHandler

from app.handlers.client.add_client_handler import AddClientHandler
from app.handlers.client.list_handler import ListClientsHandler, ListClientServiceHandler

from app.handlers.common_handler import GetAllServiceDisplayNameHandler, GetClientServiceRequestHostHandler

from app.handlers.service.list_handler import ListServicesHandler

from app.handlers.user.user_list_handler import UserListHandler
from app.handlers.user.user_handler import UserActionsHandler

class Application():

    def initialize(self, environment):

        request_settings = {
            "default_headers": {
                "Access-Control-Allow-Origin": "*",  # Adjust based on your requirements
                "Access-Control-Allow-Headers": "Content-Type",  # Adjust based on your requirements
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",  # Adjust based on your requirements
            }
        }

        app = tornado.web.Application(
            UrlMapping().get_all(),
            debug=(True if environment == Environment.DEVELOPMENT else False)
        )

        configuration = Configurations()
        app.config = configuration.initialize(environment)

        config_file = configuration.config_file
        app.settings[Key.SECRET_COOKIE_KEY] = fetch_data(config_file, Key.SECRET_COOKIE_KEY)
        print(f'\nCoookie secret key has been set successfully')

        app.settings[settings.TEMPLATE_PATH_KEY] = settings.TEMPLATE_PATH
        print(f"\nTemplate path: {settings.TEMPLATE_PATH}")
        print(f"Static path: {settings.STATIC_PATH}")

        port = fetch_data(config_file, Key.PORT, -1)
        if port != -1:
            print(f"\nListening to port:{port}")
            app.listen(port)

        return app
    
    
class UrlMapping():
    def get_all(self):
        print('\n---------- Initializing url -> handlers ----------')

        handlers = [
            (fr"{settings.STATIC_URL}", tornado.web.StaticFileHandler, {"path": settings.STATIC_PATH}),

            # (r"/.*", OptionsHandler),
            (fr"/login/success", LoginSuccessHandler),

            (fr"/client/list", ListClientsHandler),
            (fr"/client/add", AddClientHandler),
            (fr"/client/list-client-service", ListClientServiceHandler),

            (fr"/service/list", ListServicesHandler),

            (fr"/client/service/get-all", GetAllServiceDisplayNameHandler),
            (fr"/client/service/get-request-host", GetClientServiceRequestHostHandler),

            (fr"/", UserListHandler),
            # (r"/", UserActionsHandler, {"action": "list"}),
            (fr"/user/(?P<action>list|add|profile|logout)", UserActionsHandler),
        ]

        for i, handler in enumerate(handlers):
            print(f'{i+1}. {handler[0]} -> {self.get_handler_name(handler[1])}')

        return handlers

    def get_handler_name(self, _class):
        class_name = re.search(r"'(.*?)'", str(_class)).group(1)
        return str(class_name)

