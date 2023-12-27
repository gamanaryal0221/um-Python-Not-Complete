import tornado.web
import tornado.ioloop

from app.interceptors import Interceptors

import json

from app.utils.constants import Mysql
from app.utils.db_utils import get_connection

from app.utils.constants import Template, Key
from app.utils.common import get_mapped_records, get_count_from_cursor, get_total_pages, get_offset

from app.settings import BASE_LOCATION

class ListServicesHandler(tornado.web.RequestHandler):
    
    @Interceptors.session_interceptor
    async def get(self):
        
        # add_service_popup = self.ren(Template.ADD_SERVICE_POPUP)
        # print("\n\n")
        # print(add_service_popup)
        # print("\n\n")

        # popup_content = None
        # with open(BASE_LOCATION + "\\app\\templates\\service\\add_popup.html", "r", encoding="utf-8") as f:
        #     popup_content = f.read()
        #     print(popup_content)
        
        # print("\n\n")
        
        self.render(Template.LIST_SERVICES)

    
    @Interceptors.session_interceptor
    async def post(self):
        print("\\nGetting list of services...")
        
        try:
            data = json.loads(self.request.body.decode('utf-8'))
            print(data)

            page_number = int(data.get(Key.PAGE_NUMBER))
            limit = int(data.get(Key.LIMIT))
            sort_by = data.get(Key.SORT_BY)

            connection = None
            try:
                connection = get_connection(self, Mysql.USER_MANAGEMENT)
                cursor = connection.cursor()

                filter_query, filter_params = self.get_filter_query_and_params(data)

                response = {}

                cursor.execute(f"select count(*) from service s where s.soft_deleted=0 {filter_query} ", filter_params)
                response[Key.TOTAL_RECORDS] = get_count_from_cursor(cursor)
                
                params = [limit, get_offset(page_number, limit)]
                if filter_params: params = filter_params + params
                
                cursor.execute(
                    f"select s.id as {Key.ID}, s.name as {Key.NAME}, s.display_name as {Key.DISPLAY_NAME} " +
                    f"from service s where s.soft_deleted=0 {filter_query} " +
                    f" {f'order by {sort_by} ' if sort_by else '' } " +
                    "limit %s offset %s ",
                    params
                )
                services = get_mapped_records(cursor)

                response[Key.SERVICES] = services if services else []
                response[Key.TOTAL_PAGES] = get_total_pages(response[Key.TOTAL_RECORDS], limit)

                self.finish(response)
                
            except Exception as e:
                print(f"Error occured while fetching list of services {e}")
                self.finish({Key.MESSAGE:"Error occured while fetching list of services"})

            finally:
                if connection: connection.close()
        
        except Exception as e:
            print(f"Error encountered while parsing json: {e} ")
            self.finish({Key.MESSAGE:"Error encountered while parsing json"})
            return


    def get_filter_query_and_params(_self, data):
        
        id = data.get(Key.ID, None)
        name = data.get(Key.NAME, None)
        display_name = data.get(Key.DISPLAY_NAME, None)

        filter_query = ""
        filter_params = []

        if id:
            filter_query = " and s.id like %s "
            filter_params.append(f"%{id}%")

        if name:
            filter_query += " and s.name like %s"
            filter_params.append(f"%{name}%")

        if display_name:
            filter_query += " and s.display_name like %s"
            filter_params.append(f"%{display_name}%")

        return filter_query, filter_params


