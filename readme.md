# How to set up the project

    1. Clone the repository
    2. Run ```pip install .```
    3. Now the package is installed. You can run the script with the following commands:
        1. `fetch`: This command can be used to fetch emails from the Mail box. It would fetch all the new emails from the last run or all the emails on the first run and store them in the db.
        2. `action`: This command can be used to take action on the basis of rules stored in `/config/rules.json`. This will in turn call the Gmail REST API to take action as suggested in `/config/config.ini`.

# How to change configuration for the project

    - The following configurations can be made in `config.ini` file
        1. COLLECTION_PREDICATE: This can be set as `AND` and `OR`. `AND` will pick up all the rules from `rules.json` file and search for emails in db which satisfy all the rules while `OR` will pick the rules and seatrch for emails which satisfy any of these rules.
        2. ACTION: This can be set as `UNREAD`, `READ` or `MOVE`. The brief explanation of each rules is below:
            - `UNREAD`: This action will mark the email in the mailbox as Unread.
            - `READ`: This action will mark the email as read in the mailbox.
            - `MOVE`: This action will move the email to the desired folder which can be setup in the section of `MOVE` in the config file.
