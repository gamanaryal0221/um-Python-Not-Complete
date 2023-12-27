from app.utils.constants import Key, Template, Config, Environment
from app.utils.custom_exceptions import NotFoundInApplicationException

import re


def get_environment(_self, actual=True):
    environment = _self.application.config[Environment.KEY]
    if environment:
        if actual:
            return environment
        else:
            return "" if environment==Environment.PRODUCTION else environment
    else:
        raise RuntimeError(f"Could not find environment")


def render_url_not_found(self):
    render_error_page(
        self, status_code=404, title="Not Found",
        message="What you are looking for is not available."
    )

def render_error_page(self, status_code=504, title="Technical Error", message="Something went wrong\nPlease try again", redirect_url = None, redirect_text = None):
    error =  {"error":{
        Key.STATUS_CODE: status_code,
        Key.TITLE: title,
        Key.MESSAGE: message,
        Key.REDIRECT_URL: redirect_url,
        Key.REDIRECT_TEXT: redirect_text
    }}

    self.render(Template.ERROR, **error)

def get_mapped_record(cursor):
    return get_mapped_records(cursor, False)

def get_mapped_records(cursor, return_in_list=True):
    if cursor.rowcount > 0:
        all_data = cursor.fetchall()

        records = []
        columns = [column[0] for column in cursor.description]

        for data in all_data:
            record = dict(zip(columns, data))
            records.append(record)

        if len(records)==1:
            if return_in_list:
                return records
            else:
                return records[0]
        else:
            return records
    else:
        []

def get_count_from_cursor(cursor):
    all_data = cursor.fetchall()
    if all_data:
        first_record = all_data[0]
        if first_record:
            return first_record[0] if first_record[0] else 0
        else:
            return 0
    else:
        return 0
    

def redirect_to_cas_login_page(self):
    print("\nRedirecting to cas login page")
    cas_login_url = get_cas_login_url(self)
    self.redirect(cas_login_url)


def get_cas_login_url(self):
    cas_login_url = self.application.config[Config.CAS_LOGIN_URL]
    if (cas_login_url):

        host_url = self.request.full_url()
        print(f"host_url:{host_url}")

        cas_login_url = cas_login_url.replace("HOST_URL",host_url).rstrip("/")
        print(f"cas_login_url:{cas_login_url}")

        return cas_login_url

    else:
        raise NotFoundInApplicationException("CAS login url not found in application")


def refresh_all_cookies(self, payload):
    print("\nRefreshing all cookies...")
    keys = [Key.TOKEN, Key.USER_ID, Key.USERNAME, Key.FULLNAME] #Data being saved in cookies
    expires = (payload[Key.EXPIRE] if payload else 0)
    print(F"Expire cookie in {expires} hours")

    for key in keys:
        value = ""
        if payload:
            value = payload[key]
        set_cookie(self, key, value, expires)

    return True

def set_cookie(self, key, value, expires):
    print(f'Setting cookie[key:{key}, value:{value}] ...')
    self.set_secure_cookie(key, str(value), max_age=expires)

def get_cookie(self, key):
    print(f'Getting cookie for key:{key} ...')
    data = self.get_secure_cookie(key)
    return data


def fetch_data(_from, key, default_value=None):
    print(f"Reading '{key}' ...")
    if key in _from:
        return _from[key]
    else:
        if default_value:
            print(f"Missing configuration for '{key}' -> Putting {default_value} as default value")
            return default_value
        else:
            raise ImportError(f"Missing configuration for '{key}'")
        

def get_valid_selected_data_of_dropdown(data):
    return None if data=="-1" else int(data)



def is_valid_email(email):
    # Add your email validation logic here (regex, etc.)
    # For simplicity, I'm using a basic check here
    return '@' in email

def is_valid_phone(phone):
    # Add your phone validation logic here (regex, etc.)
    # For simplicity, I'm using a basic check here
    return (len(phone)==10) and phone.isdigit()

def is_valid_client_name(str):
    pattern = re.compile(r'[^a-zA-Z0-9_]')
    return bool(pattern.search(str)) or (' ' in str)


def get_total_pages(total_record, limit):
    return (total_record + limit - 1) // limit


def get_offset(page_number, limit):
    return (page_number - 1) * limit