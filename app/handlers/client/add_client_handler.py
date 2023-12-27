import tornado.web
import tornado.ioloop

from app.interceptors import Interceptors

import json

from app.utils.constants import Mysql
from app.utils.db_utils import get_connection, get_all_eligible_parent_clients, get_all_services, is_client_name_already_taken, is_vcp_id_already_taken, is_client_email_already_registered, is_client_phone_number_already_registered, get_client_by_id, get_client_email, get_client_phone_number, get_all_client_services

from app.utils.constants import Template, Key
from app.utils.common import is_valid_email, is_valid_phone, is_valid_client_name, get_valid_selected_data_of_dropdown

from app.utils.email_sender import Email

class AddClientHandler(tornado.web.RequestHandler):
    
    @Interceptors.session_interceptor
    async def get(self):

        connection = get_connection(self, Mysql.USER_MANAGEMENT)
        eligible_parent_clients = get_all_eligible_parent_clients(connection)
        services = get_all_services(connection)
        
        if connection: connection.close()
        self.render(Template.CLIENT_ADD_OR_EDIT, **{"eligible_parent_clients":eligible_parent_clients, Key.SERVICES:services})

    
    @Interceptors.session_interceptor
    async def post(self):
        print("\nAdding client ...")
        try:
            data = json.loads(self.request.body.decode('utf-8'))
            print(data)

            name = data.get(Key.NAME)
            display_name = data.get(Key.DISPLAY_NAME)
            vcp_id = data.get(Key.VCP_ID)
            parent_client_id = data.get(Key.PARENT_CLIENT_ID)
            email = data.get(Key.EMAIL)
            phone = data.get(Key.PHONE)
            is_google_authentication_enabled = data.get(Key.GOOGLE_AUTH_ENABLED)
            is_credential_authentication_enabled = data.get(Key.CREDENTIAL_AUTH_ENABLED)
            selected_service_list = data.get(Key.SERVICES, [])

            connection = None

            try:
                if not name:
                    self.finish({Key.MESSAGE:"Client name is a mandatory field"})
                    return
                else:
                    if is_valid_client_name(name):
                        self.finish({Key.MESSAGE:"Space and special characters are not allowed in client name"})
                        return

                if not display_name:
                    self.finish({Key.MESSAGE:"Client display name is a mandatory field"})
                    return

                if not vcp_id:
                    print("No VCP ID")
                    self.finish({Key.MESSAGE:"Please enter client's VCP ID."})
                    return

                if email:
                    if not is_valid_email(email):
                        print("invalid email address")
                        self.finish({Key.MESSAGE:"Please provide your valid email address"})
                        return
                else:
                    self.finish({Key.MESSAGE:"Email Address is a mandatory field"})
                    return

                if phone:
                    if not is_valid_phone(phone):
                        print("invalid phone number")
                        self.finish({Key.MESSAGE:"Please provide your valid phone number"})
                        return
                else:
                    self.finish({Key.MESSAGE:"Phone number is a mandatory field"})
                    return

                connection = get_connection(self, Mysql.USER_MANAGEMENT)
                
                if is_client_name_already_taken(connection, name):
                    self.finish({Key.MESSAGE:f"Client name '{name}' already exists"})
                    return

                if is_vcp_id_already_taken(connection, vcp_id):
                    self.finish({Key.MESSAGE:f"Sorry, '{vcp_id}' vcp id is already taken"})
                    return

                if is_client_email_already_registered(connection, email):
                    self.finish({Key.MESSAGE:f"'{email}' is already registered"})
                    return

                if is_client_phone_number_already_registered(connection, phone):
                    self.finish({Key.MESSAGE:f"'{phone}' is already registered"})
                    return

                cursor = connection.cursor()
                cursor.connection.autocommit(False)
                cursor.execute(
                    "INSERT INTO client (name, display_name, vcp_id, parent_client_id, is_google_authentication_enabled, is_credential_authentication_enabled) " +
                    "VALUES (%s, %s, %s, %s, %s, %s); ", 
                    [name, display_name, vcp_id, get_valid_selected_data_of_dropdown(parent_client_id), is_google_authentication_enabled, is_credential_authentication_enabled]
                )
                inserted_client_id = cursor.lastrowid

                if inserted_client_id:
                    print(f"Client[id:{inserted_client_id}] inserted ...")        

                    cursor.execute(
                        "INSERT INTO client_email (client_id, email, is_primary) " +
                        "VALUES (%s, %s, %s); ", 
                        [inserted_client_id, email, True]
                    )
                    print(f"Client[id:{inserted_client_id}] email[id:{cursor.lastrowid}] inserted ...")        
                    
                    cursor.execute(
                        "INSERT INTO client_number (client_id, country_code, number, is_primary) " +
                        "VALUES (%s, %s, %s, %s); ", 
                        [inserted_client_id, "+977", phone, True]
                    )
                    print(f"Client[id:{inserted_client_id}] number[id:{cursor.lastrowid}] inserted ...")        

                    if selected_service_list:
                        # Inserting into client_service
                        insert_client_service_query = "INSERT INTO client_service (client_id, service_id, request_host) VALUES (%s, %s, %s)"
                        insert_client_service_params = [
                            (inserted_client_id, service[Key.ID], service[Key.REQUEST_HOST])
                            for service in selected_service_list
                        ]
                        cursor.executemany(insert_client_service_query, insert_client_service_params)

                    
                    connection.commit()
                    self.redirect("/client/list")

                    # Run a background task to send an email to the client
                    tornado.ioloop.IOLoop.current().spawn_callback(self.send_client_created_email, inserted_client_id, display_name)
                    return

                else:
                    if connection: connection.rollback()
                    self.finish({Key.MESSAGE:"Could not add client Please try again"})
                    return


            except Exception as e:
                if connection: connection.rollback()
                print(f"Error encountered while adding client: {e} ")
                self.finish({Key.MESSAGE:"Something went wrong Please try again"})
                return
            
            finally:
                if connection: connection.close()

        except Exception as e:
            print(f"Error encountered while parsing json: {e} ")
            self.finish({Key.MESSAGE:"Something went wrong Please try again"})
            return



    async def send_client_created_email(_self, client_id, display_name):
        print (f"Sending client successfully created mail to:{display_name}")

        connection = None
        try:

            connection = get_connection(_self, Mysql.USER_MANAGEMENT)
            client = get_client_by_id(connection, client_id)
        
            client_emails = get_client_email(connection, client_id)
            client_email = client_emails[0][Key.EMAIL]
            if client_email:

                client_numbers = get_client_phone_number(connection, client_id)

                parent_client = None
                if client[Key.PARENT_CLIENT_ID]:
                    parent_client = get_client_by_id(connection, client[Key.PARENT_CLIENT_ID])

                client_services = get_all_client_services(connection, client_id)

                mail_content = _self.prepare_mail_content(client, parent_client, client_emails, client_numbers, client_services)
                is_email_sent = Email(_self).send(client_email, "Client Registered", mail_content, None)

                print(f"{'Success!' if is_email_sent else 'Failed!!!'} client successfully created email to client[id:{client_id}, display_name:{client[Key.DISPLAY_NAME]}]")
            else:
                print(f"Email not found for client[id:{client_id}, display_name:{client[Key.DISPLAY_NAME]}]")

        except Exception as e:
            print(f"Error encounered while sending client successfully created email {e}")

        finally:
            if connection: connection.close()


    def prepare_mail_content(_self, client, parent_client, client_emails, client_numbers, client_services):
        content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Client Information</title>
            </head>
            <body>

                <h2>Hello { client[Key.DISPLAY_NAME] },</h2>

                <p>Thank you for choosing our services. Below are the details for your account:</p>

                <table border="1">
                    <tr>
                        <td><strong>Client Name:</strong></td>
                        <td>{ client[Key.NAME] }</td>
                    </tr>
                    <tr>
                        <td><strong>Display Name:</strong></td>
                        <td>{ client[Key.DISPLAY_NAME] }</td>
                    </tr>
                    <tr>
                        <td><strong>VCP ID:</strong></td>
                        <td>{ client[Key.VCP_ID] }</td>
                    </tr>
                    <tr>
                        <td><strong>Parent Client :</strong></td>
                        <td>{ parent_client[Key.DISPLAY_NAME] if parent_client else 'N/A' }</td>
                    </tr>
                    <tr>
                        <td><strong>Credential Authentication Enabled:</strong></td>
                        <td>{ "Yes" if client[Key.CREDENTIAL_AUTH_ENABLED] else "No" }</td>
                    </tr>
                    <tr>
                        <td><strong>Google Authentication Enabled:</strong></td>
                        <td>{ "Yes" if client[Key.GOOGLE_AUTH_ENABLED] else "No" }</td>
                    </tr>
                </table>

                <p>Contact Information:</p>

                <ul>
                    <li>Email: { ', '.join([client_email[Key.EMAIL] for client_email in client_emails]) }</li>
                    <li>Phone Number: { ', '.join([client_number[Key.NUMBER] for client_number in client_numbers]) }</li>
                </ul>
        """

        if client_services:
            client_services_content = """
                        <p>Service URLs:</p>

                        <ul>   
                    """
            
            for client_service in client_services:
                client_services_content = client_services_content + f"""
                                        <li>{ client_service[Key.SERVICE_DISPLAY_NAME] }: { client_service[Key.REQUEST_HOST] }</li>
                                    """
                
            client_services_content = client_services_content + """
                                        </ul>
                                    """
        
        content = content + client_services_content
        content = content + """
                        <p>Feel free to reach out if you have any questions or need further assistance.</p>

                        <p>Best regards,<br>VCP</p>

                    </body>
                    </html>
                    """
        
        return content