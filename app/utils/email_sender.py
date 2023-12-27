from .constants import Config, SMTP
from .custom_exceptions import NotFoundInApplicationException

import smtplib
from email.mime.text import MIMEText

class Email():

    sender_email = None
    smtp_client = None

    def __init__(self, _self):
        print(f"Initializing SMTP service ...")

        smtp = _self.application.config[Config.SMTP]
        if smtp:

            smtp_server = smtp[SMTP.SERVER]
            smtp_port = smtp[SMTP.PORT]
            # smtp_username = smtp[SMTP_.USERNAME] # Not required in local
            # smtp_password = smtp[SMTP_.PASSWORD] # Not required in local
            sender_email = smtp[SMTP.SENDER_EMAIL]
            if sender_email:

                self.sender_email = sender_email

                try:
                    smtp_client = smtplib.SMTP(smtp_server, smtp_port)
                    # smtp_client.starttls() #Only for secured connection
                    # smtp_client.login(smtp_username, smtp_password) # Not required in local
                    self.smtp_client = smtp_client
                except Exception as e:
                    self.smtp_client = None
                    self.sender_email = None
                    print(e)
                    raise ConnectionError("Error encountered on initializing SMTP server")

            else:
                raise NotFoundInApplicationException(f"{SMTP.SENDER_EMAIL} of {Config.SMTP}")

        else:
            raise NotFoundInApplicationException(Config.SMTP)

    def send(self, to, subject, content, cc=None, bcc=None):
        print(f"\nSending mail ...")
        is_success = False

        if self.sender_email and self.smtp_client:
            msg = MIMEText(content)
            msg["Subject"] = subject
            msg["From"] = self.sender_email
            msg["To"] = to
            msg["Cc"] = cc
            msg["Bcc"] = bcc
                        
            try:
                self.smtp_client.sendmail(self.sender_email, to, msg.as_string())
                self.smtp_client.quit()
                is_success = True
            except Exception as e:
                print(f"Failed to send email: {str(e)}")

            if is_success:
                print("Email sent successfully.")
            else:
               raise RuntimeError(f"Could not send email")
        else:
            raise RuntimeError(f"Could not send email")
        
        return is_success