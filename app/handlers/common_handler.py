import tornado.web
import tornado.ioloop

from app.utils.constants import Mysql, Key
from app.utils.db_utils import get_connection, get_all_services, get_client_by_id, get_service_by_id
from app.utils.common import get_environment

import json

class GetAllServiceDisplayNameHandler(tornado.web.RequestHandler):
    def get(self):
        print ("\nFetching all services...")
        connection = get_connection(self, Mysql.USER_MANAGEMENT)
        services = get_all_services(connection)
        print (services)

        self.set_header("Content-Type", "application/json")
        self.write(json.dumps({"services": services}))


class GetClientServiceRequestHostHandler(tornado.web.RequestHandler):
    def post(self):
           
        try:
            data = json.loads(self.request.body.decode('utf-8'))

            client_id = data.get(Key.CLIENT_ID, None)
            client_name = data.get(Key.CLIENT_NAME, None)
            service_id = data.get(Key.SERVICE_ID)

            env = get_environment(self, False)
            env_in_url = f".{env}" if env else ""

            response = {Key.REQUEST_HOST:f"*{env_in_url}.vcp.com"}

            if not service_id:
                print("Service detail is not received")
                self.finish(response)
                return

            if client_id or client_name:

                connection = get_connection(self, Mysql.USER_MANAGEMENT)
                service_name = get_service_by_id(connection, service_id)[Key.NAME]

                if client_id:
                    client_name = get_client_by_id(connection, client_id)[Key.NAME]

                response[Key.REQUEST_HOST] = f"{client_name}.{service_name}"+ f"{env_in_url}.vcp.com"
                response[Key.REQUEST_HOST] = response[Key.REQUEST_HOST].replace(" ","")
                self.finish(response)
                return
                
            else:
                print("Client detail is not received")
                self.finish(response)
                return
        
        except Exception as e:
            print(f"Error encountered while parsing json: {e} ")
            self.finish(response)
            return
