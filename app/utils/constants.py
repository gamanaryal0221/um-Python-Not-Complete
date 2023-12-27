class Template():
    USER_LIST = "user/list.html"
    ERROR = "error.html"

    CLIENT_ADD_OR_EDIT = "client/add_or_edit.html"
    LIST_CLIENTS = "client/list.html"
    LIST_CLIENT_SERVICE = "client/list_client_service.html"

    LIST_SERVICES = "service/list.html"
    ADD_SERVICE_POPUP = "service/add_popup.html"


class Environment():
    KEY = "environment"
    DEVELOPMENT = "dev"
    QC = "qc"
    PRODUCTION = "prod"

class Config():
    CAS_LOGIN_URL = "cas_login_url"
    MYSQL = "mysql"
    SMTP = "smtp"


class Mysql():
    USER_MANAGEMENT = 'user_management'

    HOSTNAME = 'hostname'
    DATABASE = 'database'
    USER = 'user'
    PASSWORD = 'password'


class SMTP():
    SERVER = "server"
    PORT = "port"
    USERNAME = "username"
    PASSWORD = "password"

    SENDER_EMAIL = 'sender_email'
    

class Key():
    STATUS_CODE = "status_code"
    TITLE = "title"
    MESSAGE = "message"
    REDIRECT_URL = "redirect_url"
    REDIRECT_TEXT = "redirect_text"

    SECRET_COOKIE_KEY = "cookie_secret"

    TOKEN = "token"

    SALT_VALUE = "salt_value"
    HASHED_PASSWORD = "hashed_password"

    USER_ID = "user_id"
    USERNAME = "username"
    FULLNAME = "fullname"

    HOST_URL = "host_url"

    PORT = "port"
    
    EXPIRE = "exp"

    ID = "id"
    NAME = 'name'
    DISPLAY_NAME = 'display_name'
    VCP_ID = 'vcp_id'
    PARENT_CLIENT_ID = "parent_client_id"
    EMAIL = 'email'
    PHONE = 'phone'
    NUMBER = "number"
    GOOGLE_AUTH_ENABLED = 'is_google_authentication_enabled'
    CREDENTIAL_AUTH_ENABLED = 'is_credential_authentication_enabled'
    SERVICES = 'services'
    REQUEST_HOST = "request_host"

    OK = "ok"

    CLIENT_ID = "client_id"
    CLIENT_NAME = "client_name"
    CLIENT_DISPLAY_NAME = "client_display_name"
    SERVICE_DISPLAY_NAME = "service_display_name"
    PARENT_CLIENT_DISPLAY_NAME = "parent_client_display_name"

    SERVICE_ID = "service_id"

    CLIENTS = "clients"

    PAGE_NUMBER = "page_number"
    LIMIT = "limit"
    SORT_BY = "sort_by"
    TOTAL_RECORDS = "total_records"
    TOTAL_PAGES = "total_pages"


class Token():
    PRIVATE_KEY = "private_key"
    EXPIRE_DURATION = "expire_duration"
    ALGORITHM = "algorithm"

    DEFAULT_EXPIRE_DURATION = 8
    DEFAULT_ALGORITHM = 'HS256'

class Action:
    LIST = "list"
    PROFILE = "profile"
    LOGOUT = "logout"