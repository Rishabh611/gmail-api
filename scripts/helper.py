import os.path
import configparser
import sqlite3
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

config = configparser.ConfigParser()

# Read the config.ini file
config.read('./config/config.ini')

def email_exists(cursor, email_id):
    cursor.execute('SELECT id FROM mail WHERE id = ?', (email_id,))
    return cursor.fetchone() is not None

def fetch_creds():
        SCOPES = config['global']['SCOPE']
        creds = None
        print(SCOPES)
        if os.path.exists('./config/token.json'):
            creds = Credentials.from_authorized_user_file('./config/token.json', [SCOPES])
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    './config/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('./config/token.json', 'w') as token:
                token.write(creds.to_json())
        return creds
        

def get_last_fetch_time():
    connection = sqlite3.connect('./db/mail.db')
    cursor = connection.cursor()
    cursor.execute("Select last_run_time from script_data")
    result = cursor.fetchone()
    connection.close()
    if result:
        last_run_time_str = result[0]
        last_run_time = datetime.strptime(last_run_time_str, '%Y-%m-%d %H:%M:%S')
        last_run_time = last_run_time.strftime('%Y/%m/%d')
        return last_run_time
    else:
        return None

def db_setup():
    # Define the database filename
    print("db setup")
    # Connect to the database (it will be created if it doesn't exist)
    connection = sqlite3.connect( "./db/mail.db")
    cursor = connection.cursor()

    # Define the SQL statements to create tables
    create_table_mail_sql = """
    CREATE TABLE 'mail' ("id"	TEXT NOT NULL UNIQUE, "subject"	TEXT, "from"	TEXT NOT NULL, "date_received"	TEXT NOT NULL, "is_processed"	TEXT DEFAULT 'false', PRIMARY KEY("id") )
    """
    cursor.execute(create_table_mail_sql)
    connection.commit()
    create_table_script_data_sql = """
    CREATE TABLE "script_data" (
        "last_run_time"	TEXT
    )

    """

    # Execute the SQL statements to create tables
    
    cursor.execute(create_table_script_data_sql)

    # Commit the changes and close the connection
    connection.commit()
    connection.close()

    return True