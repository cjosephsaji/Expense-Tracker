# Expense Tracker

Telegram Bot which tracks user expenses monthly


## Setup
1. ``pip install -r requirements.txt``
2. Add your *Telegram Bot API* to **.env** acquired from *Bot Father*
3. Uncomment and set your *Telegram User ID* to **core.py** in **line 16**
4. After running the bot, use the ``/startmonthlyreport`` command to send monthly reports to the users automatically

## Addtional Currencies
If you wish to add more currencies, head over to **other/other.json** and add your preferred currency

## Addtional words for commands
If you wish to add more synonyms words to the commands ``add``, ``remove``, ``currency`` and ``custom_report``, head over to **commandsdata/commands.json** and add to your preference

``{"similar_word" : "command"}``

Example : 

``{"addionalproduct" : "add"}``
