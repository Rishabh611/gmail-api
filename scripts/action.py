import requests, os
import sqlite3
import json
from datetime import datetime, timedelta
import configparser
import logging  # Import the logging module
from .helper import fetch_creds, db_setup
log_directory = './logs/'

# Ensure the log directory exists; create it if it doesn't
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
log_file_path = './logs/action_script.log'

# Check if the log file exists
if not os.path.isfile(log_file_path):
    # If the file doesn't exist, create it (the 'w' mode will create a new file if it doesn't exist)
    with open(log_file_path, 'w') as file:
        # Optionally, write an initial message to the log file
        file.write('Log file created.')
# Configure the logging
logging.basicConfig(filename='./logs/action_script.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def apply_rules(rule):
    field = rule["field"]
    predicate = rule["predicate"]
    value = rule["value"]

    if field == "subject":
        if predicate == "contains":
            return f"{field} LIKE '%{value}%'"
        elif predicate == "does not contain":
            return f"{field} NOT LIKE '%{value}%'"
        elif predicate == "equals":
            return f"{field} = '{value}'"
        elif predicate == "does not equal":
            return f"{field} != '{value}'"
    elif field == "from":
        if predicate == "contains":
            return f"`{field}` LIKE '%{value}%'"
        elif predicate == "does not contain":
            return f"`{field}` NOT LIKE '%{value}%'"
        elif predicate == "equals":
            return f"`{field}` = '{value}'"
        elif predicate == "does not equal":
            return f"`{field}` != '{value}'"
    elif field == "date_received":
        if predicate == "less than days":
            days_ago = datetime.now() - timedelta(days=int(value))
            return f"{field} > '{days_ago.strftime('%Y-%m-%d %H:%M:%S')}'"
        elif predicate == "greater than days":
            days_ago = datetime.now() - timedelta(days=int(value))
            return f"{field} < '{days_ago.strftime('%Y-%m-%d %H:%M:%S')}'"
        elif predicate == "less than months":
            months_ago = datetime.now() - timedelta(days=int(value) * 30)
            return f"{field} > '{months_ago.strftime('%Y-%m-%d %H:%M:%S')}'"
        elif predicate == "greater than months":
            months_ago = datetime.now() - timedelta(days=int(value) * 30)
            return f"{field} < '{months_ago.strftime('%Y-%m-%d %H:%M:%S')}'"
def main():
    # Load configuration from config.ini
    if not os.path.exists('./db/mail.db'):
        db_setup()
    config = configparser.ConfigParser()
    config.read('./config/config.ini')
    collection_predicate = config['global']['COLLECTION_PREDICATE']
    logging.info(f"The predicate for collection of rules is {collection_predicate}")
    # Load rules from rules.json
    with open('./config/rules.json', 'r') as json_file:
        rules = json.load(json_file)
    logging.info(f"Total {len(rules)} rules found.")
    # Connect to the SQLite database
    conn = sqlite3.connect('./db/mail.db')
    cursor = conn.cursor()

    # Build the SQL query based on rules and collection predicate
    sql_query = "SELECT id FROM mail WHERE is_processed=\"false\" AND "
    for rule in rules:
        sql_query += apply_rules(rule)
        sql_query += f" {collection_predicate[1:-1]} "

    if collection_predicate == "AND":
        sql_query = sql_query[:-5]
    else:
        sql_query = sql_query[:-4]

    cursor.execute(sql_query)
    result = cursor.fetchall()
    try:
        cred = fetch_creds()
        if not cred:
            raise Exception("There's error in fetching creds")
        access_token = cred.token
    
    

        # Gmail API configurations
        api_url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages/'
        api_key = config['global']['API_KEY']

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        # Process messages based on action
        action = config["global"]["ACTION"]

        if action == "MOVE":
            payload = {
                "addLabelIds": [
                    config["MOVE"]["LABEL"]
                ],
            }
        elif action == "READ":
            payload = {
                "removeLabelIds": [
                    "UNREAD"
                ],
            }
        elif action == "UNREAD":
            payload = {
                'addLabelIds': ['UNREAD']
            }

        logging.info(f"Total {len(result)} new emails found satisfying the rules.")
        logging.info(f"Action {action} configured for the filtered emails.")
        for msg_id in list(result):
            msg_id = msg_id[0]
            # Make a POST request to modify the message
            response = requests.post(api_url + msg_id + "/modify" + "?key=" + api_key, json=payload, headers=headers)

            if response.status_code == 200:
                cursor.execute(f"UPDATE mail SET is_processed = \"true\" WHERE id = \"{msg_id}\"")
                logging.info(f"Action on email with id {msg_id} was taken successfully.")
            elif response.status_code == 404:
                logging.error('The requested resource was not found. Status code:', response.status_code)
            else:
                logging.error('An error occurred. Status code:', response.status_code)
    except Exception as e:
        logging.error(f"An error occured: {str(e)}")

    # Commit changes to the database and close the connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()
