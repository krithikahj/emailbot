Email Bot

This is a lightweight Python automation script, and I'm trying to solve a very unique use case specific to me. I like reading and scanning my emails and have anxiety about randomly automating it completely to delete or reply without verifying first; however, I receive a lot of statements and automated emails that I know that I tend to delete but I can't unsubscribe from. This is a lightweight tool to declutter my inbox by automatically opening some banking alerts and deleting repetitive receipts or marketing reminders.

## Features

* **Weekly Automation:** It runs automatically on my system once a week.
* **Seven-Day Scan:** It will go through my unread email, pull the last email from the last seven days, and go through them.
* **Categorization Engine:** It uses a `config.json` file with specific rules to determine which emails should be opened and which should be deleted.
* **Safety Shield:** I also have some safety words to ensure the script does not touch specific sensitive emails.
* **Peeking Mode:** We're also "peeking" to prevent opening all of my emails, because there will be other emails that I'll still want to read.
* **Unread Preservation:** If an email doesn't match either the open or delete rules, the script ensures it remains marked as "Unread."

## Setup

1. **Python & App Password:** Install Python and go to your Google Account security settings to generate an **App Password**.
2. **Environment File:** Create a file named `.env` in the root folder of the project.
3. **Configure Credentials:** Inside the `.env` file, add your details exactly like this:

```env
EMAIL_USER="your-email@gmail.com"
EMAIL_PASS="your-16-character-app-password"

```

4. **Run:** Customize your `config.json` and run the script:
```bash
python3 cleaninbox.py

```