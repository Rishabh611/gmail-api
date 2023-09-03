from __future__ import print_function
import sqlite3
import os
import datetime
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging  # Import the logging module
from .helper import email_exists, fetch_creds, get_last_fetch_time, db_setup

log_file_path = './logs/fetch_script.log'

# Check if the log file exists
if not os.path.isfile(log_file_path):
    # If the file doesn't exist, create it (the 'w' mode will create a new file if it doesn't exist)
    with open(log_file_path, 'w') as file:
        # Optionally, write an initial message to the log file
        file.write('Log file created.')
# Configure the logging
logging.basicConfig(filename='./logs/fetch_script.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    creds = fetch_creds()
    if not creds:
        raise Exception("Error in fetching creds")
    logging.info("Creds fetched")
    
    try:
        service = build('gmail', 'v1', credentials=creds)
        print(os.path.exists('./db/mail.db'))
        if not os.path.exists('./db/mail.db'):
            db_setup()
        last_run_time = get_last_fetch_time()
        logging.info(f"Last run time of script {last_run_time}")
        if last_run_time:
            search_query = f"after:{last_run_time}"
            results = service.users().messages().list(userId='me', q=search_query).execute()
        else:
            results = service.users().messages().list(userId='me',).execute()
       
        connection = sqlite3.connect('./db/mail.db')
        cursor = connection.cursor()
        messages = results.get('messages', [])
        logging.info(f"Emails fetched. Total {len(messages)} new email found.")
        for message in messages:
            msg_id = message['id']
            if not email_exists(cursor, msg_id):
                msg = service.users().messages().get(userId='me', id=msg_id).execute()
                subject = ''
                sender = ''
                date_received = ''
                for header in msg['payload']['headers']:
                    if header['name'] == 'Subject':
                        subject = header['value']
                    elif header['name'] == 'From':
                        sender = header['value']
                    elif header['name'] == 'Date':
                        date_received = header['value']
                cursor.execute('INSERT INTO mail VALUES (?, ?, ?, ?,?)', (msg_id, subject, sender, date_received, "false"))
                logging.info("New email inserted in the db.")
        if last_run_time:
            cursor.execute('UPDATE script_data SET last_run_time = ? WHERE rowid = 1', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
        else:
            cursor.execute("INSERT INTO script_data VALUES(?)", (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
        connection.commit()
        connection.close()

    except HttpError as error:
        logging.error(f'An error occurred: {error}')
        print(f'An error occurred: {error}')

    except sqlite3.Error as sqlite_error:
        logging.error(f'SQLite error: {sqlite_error}')
        print(f'SQLite error: {sqlite_error}')

    except Exception as e:
        logging.error(f'An unexpected error occurred: {e}')
        print(f'An unexpected error occurred: {e}')

if __name__ == '__main__':
    main()
