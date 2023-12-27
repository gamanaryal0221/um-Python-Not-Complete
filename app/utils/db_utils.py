import pymysql

from .constants import Config
from .custom_exceptions import NotFoundInApplicationException

from .common import get_mapped_record, get_mapped_records, get_count_from_cursor, fetch_data
from .constants import Key, Mysql

def get_connection(_self, server_key):
    if server_key:
        print(f"\nEstablishing new connection with {server_key}")
        mysql_servers = _self.application.config[Config.MYSQL]
        if server_key in mysql_servers:
            mysql_server = fetch_data(mysql_servers, server_key)

            connection = None

            try:
                connection = pymysql.connect(
                    host = fetch_data(mysql_server, Mysql.HOSTNAME),
                    database = fetch_data(mysql_server, Mysql.DATABASE),
                    user = fetch_data(mysql_server, Mysql.USER),
                    password = fetch_data(mysql_server, Mysql.PASSWORD)
                )
            except Exception as e:
                print(e)

            if connection:
                print(f"Successfully connected with '{server_key}'")
                return connection
            else:
                raise ConnectionError(f"Could not connect with '{server_key}'")
            
        else:
            raise RuntimeError(f"Could not find connection detail[server:'{server_key}']")
    else:
        raise NotFoundInApplicationException(f" {server_key} in {Config.MYSQL}")

  
def is_client_name_already_taken(conn, client_name):
    cursor = conn.cursor()
    cursor.execute("select count(*) from client where name=%s", [client_name])
    client_name_count = get_count_from_cursor(cursor)
    cursor.close()
    return False if client_name_count==0 else True

  
def is_vcp_id_already_taken(conn, registered_id):
    cursor = conn.cursor()
    cursor.execute("select count(*) from client where vcp_id=%s", [registered_id])
    registered_id_count = get_count_from_cursor(cursor)
    cursor.close()
    return False if registered_id_count==0 else True

def is_client_email_already_registered(conn, email):
    return _is_email_already_registered(conn, "client", email)

def is_client_phone_number_already_registered(conn, phone_number):
    return _is_phone_number_already_registered(conn, "client", phone_number)

def _is_email_already_registered(conn, _for, email):
    return _is_email_or_phone_already_registered(conn, _for, "email", email)

def _is_phone_number_already_registered(conn, _for, phone_number):
    return _is_email_or_phone_already_registered(conn, _for, "number", phone_number)
    
def _is_email_or_phone_already_registered(conn, _for, what, email_phone):
    cursor = conn.cursor()
    cursor.execute(
        f"select count(*) from {_for}_{what} where {what} " +
        "=%s", [email_phone]
        )
    email_phone_count = get_count_from_cursor(cursor)
    cursor.close()
    return False if email_phone_count==0 else True




def get_client_email(conn, id, only_primary=False):
    return _get_email(conn, id, "client", only_primary)

def get_client_phone_number(conn, id, only_primary=False):
    return _get_phone_number(conn, id, "client", only_primary)

def _get_email(conn, id, _for, only_primary):
    return _get_email_or_phone(conn, id, _for, "email", only_primary)

def _get_phone_number(conn, id, _for, only_primary):
    return _get_email_or_phone(conn, id, _for, "number", only_primary)

def _get_email_or_phone(conn, id, _for, what, only_primary):
    cursor = conn.cursor()

    plus_sql = ""
    if only_primary:
        plus_sql = " and is_primary=true "

    cursor.execute(
        f"select {what}, is_primary from {_for}_{what} where {_for}_id" +
        "=%s "
        f" {plus_sql} ",
        [id]
    )

    if only_primary:
        cursor.close()
        return get_mapped_record(cursor)
    else:
        cursor.close()
        return get_mapped_records(cursor)
    

def get_client_by_id(conn, client_id):
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"select name, display_name, vcp_id, parent_client_id, is_credential_authentication_enabled, is_google_authentication_enabled "
            "from client " +
            "where soft_deleted=0 and id=%s ; ",
            [client_id]
        )
        client = get_mapped_record(cursor)
        cursor.close()
        return client
    except Exception as e:
        print(f"Error encountered while fetching client by id:{client_id} : {e}")
        return None
    

def get_service_by_id(conn, service_id):
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"select name as {Key.NAME}, display_name as {Key.DISPLAY_NAME} from service " +
            "where soft_deleted=0 and id=%s ; ",
            [service_id]
        )
        service = get_mapped_record(cursor)
        cursor.close()
        return service
    except Exception as e:
        print(f"Error encountered while fetching service by id:{service_id} : {e}")
        return None


def get_all_eligible_parent_clients(conn):
    try:
        cursor = conn.cursor()
        cursor.execute(f"select id, vcp_id, display_name from client where soft_deleted=0 and (parent_client_id is null or parent_client_id='') ; ")
        eligible_parent_clients = get_mapped_records(cursor)
        cursor.close()
        return eligible_parent_clients if eligible_parent_clients else []
    except Exception as e:
        print(f"Error encountered while fetching all eligible parent clients: {e}")
        return None


def get_all_services(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("select id, display_name from service where soft_deleted=0 ")
        services = get_mapped_records(cursor)
        cursor.close()
        return services if services else []
    except Exception as e:
        print(f"Error encountered while fetching all services: {e}")
        return None



def get_all_client_services(conn, filter_client_id=None, filter_service_id=None):
    try:

        filter_client_service_sql = None
        params = []
        if filter_client_id:
            filter_client_service_sql = " c.id=%s "
            params = [filter_client_id]

        if filter_service_id:
            if filter_client_id:
                filter_client_service_sql = filter_client_service_sql + " and s.id=%s "
                params.append(filter_service_id)
            else:
                filter_client_service_sql = " s.id=%s "
                params = [filter_service_id]


        cursor = conn.cursor()
        cursor.execute(
            f"select c.display_name as {Key.CLIENT_DISPLAY_NAME}, s.display_name as {Key.SERVICE_DISPLAY_NAME}, cs.request_host as {Key.REQUEST_HOST} from client_service cs " +
            "inner join client c on c.id=cs.client_id " +
            "inner join service s on s.id=cs.service_id "
            f" {f'where {filter_client_service_sql}' if filter_client_service_sql else ''} ",
            params
        )
        client_services = get_mapped_records(cursor)
        cursor.close()
        return client_services if client_services else []
    except Exception as e:
        print(f"Error encountered while fetching client services[filter_client_id:{filter_client_id}, filter_service_id:{filter_service_id}]: {e}")
        return None


