from app import settings
import json

from app.utils.constants import Config, Mysql, SMTP, Environment
import pymysql

from app.utils.custom_exceptions import MissingConfigException, NothingFoundInConfigException


class Configurations():

    config_file = None

    def __init__(self):
        print('\n---------- Initializing configuration ----------')
        config_file = self._read_configuration()
        if config_file:
            self.config_file = config_file
        else:
            raise Exception("Could not read config file")

    def initialize(self, environment):
        config = {Environment.KEY: environment}

        config[Config.CAS_LOGIN_URL] = self._fetch_data(self.config_file, Config.CAS_LOGIN_URL)
        print (f"{Config.CAS_LOGIN_URL.upper().replace('_',' ')} = {config[Config.CAS_LOGIN_URL]}")
        config[Config.MYSQL] = self._collect_sql_data()
        config[Config.SMTP] = self._collect_smtp_detail_to_send_email()

        return config
    
     
    def _read_configuration(self):
        config_path = settings.CONFIG_PATH+'\\'+settings.CONFIG_FILE_NAME
        print(f'\nReading config file from {config_path} ...')

        config_file = None
        try:
            with open(config_path, 'r') as file:
                config_file = json.load(file)
        except Exception as e:
            print(e)

        return config_file
    


    def _collect_sql_data(self):
        print(f"\nCollecting mysql server details ----------")
        mysql_servers = self._fetch_data(self.config_file, Config.MYSQL)
        if mysql_servers:
            mysql_server = {}
            mysql_server[Mysql.USER_MANAGEMENT] = self._collect_mysql_data_and_test_connection(Mysql.USER_MANAGEMENT, mysql_servers)

            return mysql_server
        else:
            raise NothingFoundInConfigException(Config.MYSQL)

        
    def _establish_mysql_connection(self, server_key, mysql_servers):
        mysql_server = self._fetch_data(mysql_servers, server_key)
        if mysql_server:        
            print(f'Connecting with \'{server_key}\' ...')
            connection = None

            try:
                connection = pymysql.connect(
                    host=mysql_server[Mysql.HOSTNAME],
                    database=mysql_server[Mysql.DATABASE],
                    user=mysql_server[Mysql.USER],
                    password=mysql_server[Mysql.PASSWORD]
                )
            except Exception as e:
                print(e)

            if connection:
                print(f"Successfully connected with '{server_key}'")
                return connection
            else:
                raise ConnectionError(f"Could not connect with '{server_key}'")
            
        else:
            raise NothingFoundInConfigException(server_key)
        
    
    def _collect_mysql_data_and_test_connection(self, server_key, mysql_servers):
        mysql_server = self._fetch_data(mysql_servers, server_key)
        if mysql_server:

            host = self._fetch_data(mysql_server, Mysql.HOSTNAME)
            db = self._fetch_data(mysql_server, Mysql.DATABASE)
            user = self._fetch_data(mysql_server, Mysql.USER)
            password = self._fetch_data(mysql_server, Mysql.PASSWORD)

            print(f'Connecting with \'{server_key}\' ...')
            connection = None
            try:
                connection = pymysql.connect(host=host, database=db, user=user, password=password)
            except Exception as e:
                print(e)

            if connection:
                print(f"Successfully connected with '{server_key}'")
                connection.close()
                return {
                    Mysql.HOSTNAME: host,
                    Mysql.DATABASE: db,
                    Mysql.USER: user,
                    Mysql.PASSWORD: password
                }
            else:
                raise ConnectionError(f"Could not connect with '{server_key}'")
            
        else:
            raise NothingFoundInConfigException(server_key)



    def _collect_smtp_detail_to_send_email(self):
        print('\n---------- Getting SMTP details ----------')
        smtp = self._fetch_data(self.config_file, Config.SMTP)
        if smtp:
            return {
                SMTP.SERVER: self._fetch_data(smtp, SMTP.SERVER),
                SMTP.PORT: self._fetch_data(smtp, SMTP.PORT),
                SMTP.USERNAME: self._fetch_data(smtp, SMTP.USERNAME),
                SMTP.PASSWORD: self._fetch_data(smtp, SMTP.PASSWORD),
                SMTP.SENDER_EMAIL: self._fetch_data(smtp, SMTP.SENDER_EMAIL)
            }
        else:
            raise NothingFoundInConfigException(Config.SMTP)
        

    def _fetch_data(self, _from, key, default_value=None):
        print(f"Reading '{key}' ...")
        if key in _from:
            return _from[key]
        else:
            if default_value:
                print(f"Missing configuration for '{key}' -> Putting {default_value} as default value")
                return default_value
            else:
                raise MissingConfigException(key)