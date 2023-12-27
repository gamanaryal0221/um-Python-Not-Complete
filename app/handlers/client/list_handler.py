import tornado.web
import tornado.ioloop

import json

from app.interceptors import Interceptors

from app.utils.constants import Mysql
from app.utils.db_utils import get_connection

from app.utils.constants import Template, Key
from app.utils.common import get_mapped_records, get_count_from_cursor, get_total_pages, get_offset

class ListClientsHandler(tornado.web.RequestHandler):
    
    @Interceptors.session_interceptor
    async def get(self):
        self.render(Template.LIST_CLIENTS)

    
    @Interceptors.session_interceptor
    async def post(self):
        print("\nGetting list of clients...")
        
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

                filter_query, filter_params = self.get_filter_query_and_params(data, connection)

                response = {}

                cursor.execute(f"select count(*) from client c where c.soft_deleted=0 {filter_query} ", filter_params)
                response[Key.TOTAL_RECORDS] = get_count_from_cursor(cursor)
                
                params = [limit, get_offset(page_number, limit)]
                if filter_params: params = filter_params + params
                
                cursor.execute(
                    f"select c.id as {Key.ID}, c.name as {Key.NAME}, c.display_name as {Key.DISPLAY_NAME}, c.vcp_id as {Key.VCP_ID}, c.parent_client_id as {Key.PARENT_CLIENT_ID}, " +
                    f"(case when c.parent_client_id is null or c.parent_client_id='' then '' else (select c1.display_name from client c1 where c1.id=c.parent_client_id) end ) as {Key.PARENT_CLIENT_DISPLAY_NAME} "
                    f"from client c where c.soft_deleted=0 {filter_query} " +
                    f" {f'order by {sort_by} ' if sort_by else '' } " +
                    "limit %s offset %s ",
                    params
                )
                clients = get_mapped_records(cursor)

                response[Key.CLIENTS] = clients if clients else []
                response[Key.TOTAL_PAGES] = get_total_pages(response[Key.TOTAL_RECORDS], limit)

                # response = self.get_response(connection, page_number, limit)
                self.finish(response)
                
            except Exception as e:
                print(f"Error occured while fetching list of clients {e}")
                self.finish({Key.MESSAGE:"Error occured while fetching list of clients"})

            finally:
                if connection: connection.close()
        
        except Exception as e:
            print(f"Error encountered while parsing json: {e} ")
            self.finish({Key.MESSAGE:"Error encountered while parsing json"})
            return


    def get_filter_query_and_params(_self, data, conn):
        
        id = data.get(Key.ID, None)
        name = data.get(Key.NAME, None)
        display_name = data.get(Key.DISPLAY_NAME, None)
        vcp_id = data.get(Key.VCP_ID, None)
        parent_client_display_name = data.get(Key.PARENT_CLIENT_DISPLAY_NAME, None)

        filter_query = ""
        filter_params = []

        if id:
            filter_query = " and c.id like %s "
            filter_params.append(f"%{id}%")

        if name:
            filter_query += " and c.name like %s"
            filter_params.append(f"%{name}%")

        if display_name:
            filter_query += " and c.display_name like %s"
            filter_params.append(f"%{display_name}%")

        if vcp_id:
            filter_query += " and c.vcp_id like %s"
            filter_params.append(f"%{vcp_id}%")

        
        if parent_client_display_name:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "select c.id from client c " +
                    "inner join client c1 on c1.id=c.parent_client_id "
                    "where c1.display_name like %s ",
                    [f"%{parent_client_display_name}%"]
                )
                parent_client_id_list = [record[0] for record in cursor.fetchall()]
                cursor.close()

                if parent_client_id_list:
                    print(parent_client_id_list)
                    filter_query = filter_query + " and c.id in ({}) ".format(','.join(['%s' for _ in parent_client_id_list]))
                    filter_params = filter_params + parent_client_id_list
            except Exception as e:
                print(f"Error encountered while searching parent client display name : {e} ")
                return None, None
            
        return filter_query, filter_params




class ListClientServiceHandler(tornado.web.RequestHandler):
    
    @Interceptors.session_interceptor
    async def get(self):
        self.render(Template.LIST_CLIENT_SERVICE)

    
    @Interceptors.session_interceptor
    async def post(self):
        print("\nGetting list client-services...")
        
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

                cursor.execute(
                    "select count(*) from client_service cs " +
                    "inner join client c on c.id=cs.client_id " +
                    f"inner join service s on s.id=cs.service_id {filter_query}", 
                    filter_params
                )
                response[Key.TOTAL_RECORDS] = get_count_from_cursor(cursor)
                
                params = [limit, get_offset(page_number, limit)]
                if filter_params: params = filter_params + params
                
                cursor.execute(
                    f"select c.id as {Key.CLIENT_ID}, c.name as {Key.CLIENT_NAME}, c.display_name as {Key.CLIENT_DISPLAY_NAME}, " +
                    f"s.id as {Key.SERVICE_ID}, s.display_name as {Key.SERVICE_DISPLAY_NAME}, cs.request_host as {Key.REQUEST_HOST} " +
                    "from client_service cs " +
                    "inner join client c on c.id=cs.client_id " +
                    f"inner join service s on s.id=cs.service_id {filter_query} " +
                    f" {f'order by {sort_by} ' if sort_by else '' } " +
                    "limit %s offset %s ",
                    params
                )
                client_service_list = get_mapped_records(cursor)

                response["client_service_list"] = client_service_list if client_service_list else []
                response[Key.TOTAL_PAGES] = get_total_pages(response[Key.TOTAL_RECORDS], limit)

                self.finish(response)
                
            except Exception as e:
                print(f"Error occured while fetching list of client-services {e}")
                self.finish({Key.MESSAGE:"Error occured while fetching list of client-services"})

            finally:
                if connection: connection.close()
        
        except Exception as e:
            print(f"Error encountered while parsing json: {e} ")
            self.finish({Key.MESSAGE:"Error encountered while parsing json"})
            return


    def get_filter_query_and_params(_self, data):
        
        client_name = data.get(Key.CLIENT_NAME, None)
        client_display_name = data.get(Key.CLIENT_DISPLAY_NAME, None)
        service_display_name = data.get(Key.SERVICE_DISPLAY_NAME, None)
        request_host = data.get(Key.REQUEST_HOST, None)

        filter_query = ""
        filter_params = []

        if client_name:
            filter_query = " c.name like %s "
            filter_params.append(f"%{client_name}%")

        if client_display_name:
            filter_query += " and c.display_name like %s"
            filter_params.append(f"%{client_display_name}%")

        if service_display_name:
            filter_query += " and s.display_name like %s"
            filter_params.append(f"%{service_display_name}%")

        if request_host:
            filter_query += " and cs.request_host like %s"
            filter_params.append(f"%{request_host}%")

        if filter_query.startswith(" and"):
            filter_query = filter_query[len(" and"):]

        return (f" where {filter_query}" if filter_query else ""), filter_params
