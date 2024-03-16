import json
from telebot.util import quick_markup
import datetime



async def open_json_data(filepath, functiontype, data_to_write=''):
    file = open(filepath, functiontype)
    if functiontype == 'r':
        data = json.load(file)
        return data
    else:
        data = json.dump(data_to_write, file)
    file.close()

async def check_auth_user(id):
    file = open('authdata/authorized_users.json')
    users_auth = json.load(file)
    file.close()
    if str(id) in users_auth:
        return True
    
async def confirm_request_auth():
    markup = quick_markup({
        'Yes': {'callback_data': 'request_auth_y'},
        'No': {'callback_data': 'request_auth_n'},
    }, row_width=2)
    return markup

async def create_auth_user(data, functiontype=''):
    if functiontype == 'admit_request':
        markup = quick_markup({
            'Admit': {'callback_data': f'confirm_auth_y_{data.from_user.id}'},
            'Reject': {'callback_data': f'reject_auth_n_{data.from_user.id}'},
        }, row_width=2)
        return markup
    elif functiontype == 'awaiting_entry':
        awaiting_users = await open_json_data('authdata/awaiting_authorization.json', 'r')
        awaiting_users.update({str(data.from_user.id): data.from_user.username})
        await open_json_data('authdata/awaiting_authorization.json', 'w', awaiting_users)
    elif functiontype == 'user_admitted':
        awaiting_users = await open_json_data('authdata/authorized_users.json', 'r')
        awaiting_users.update(data)
        accounts_data = await open_json_data('findata/monthlydata.json', 'r')
        month_year = datetime.datetime.now().strftime("%B") + ' ' + datetime.datetime.now().strftime("%Y")
        accounts_data['Accounts'][month_year][list(data)[0]] = {'currency' : '', 'Items' : {}}
        await open_json_data('findata/monthlydata.json', 'w', accounts_data)
        await open_json_data('authdata/authorized_users.json', 'w', awaiting_users)
        awaiting_users = await open_json_data('authdata/awaiting_authorization.json', 'r')
        for key in data.keys():
            user_admitted = key
            del awaiting_users[user_admitted]
        await open_json_data('authdata/awaiting_authorization.json', 'w', awaiting_users)
    elif functiontype == 'user_rejected':
        awaiting_users = await open_json_data('authdata/awaiting_authorization.json', 'r')
        del awaiting_users[data]
        await open_json_data('authdata/awaiting_authorization.json', 'w', awaiting_users)
    elif functiontype == 'remove_user':
        awaiting_users = await open_json_data('authdata/authorized_users.json', 'r')
        username = data.split('@')
        for key,value in awaiting_users.items():
            if value == username[-1].strip():
                del awaiting_users[key]
                break
        await open_json_data('authdata/authorized_users.json', 'w', awaiting_users)
    elif functiontype == 'ban_user':
        banned_users = await open_json_data('authdata/banned_users.json', 'r')
        user_to_ban = data.split("@")
        banned_users[user_to_ban[-1]] = None
        await open_json_data('authdata/banned_users.json', 'w', banned_users)
    elif functiontype == 'unban_user':
        banned_users = await open_json_data('authdata/banned_users.json', 'r')
        user_to_unban = data.split('@')
        del banned_users[user_to_unban[-1]]
        await open_json_data('authdata/banned_users.json', 'w', banned_users)


async def check_banned_users(user):
    banned_users = await open_json_data('authdata/banned_users.json', 'r')
    if user in banned_users:
        return True
    else:
        return False
    

async def currency(user_id, currency_data=""):
    month_year = datetime.datetime.now().strftime("%B %Y")
    if currency_data == "":
        json_data = await open_json_data('findata/monthlydata.json', 'r')
        if json_data['Accounts'][month_year][str(user_id)]['currency'] != '':
            return True
    elif currency_data == "setting":
        currency_data_to_send = ""
        json_data = await open_json_data('other/other.json', 'r')
        for currency in json_data["currency"]:
            currency_data_to_send += f"`currency {currency['name']}` ({currency['symbol']})\n\n"
        currency_data_to_send += "\n\n\nPlease set your currency first by clicking on any of the desired and sending it to me"
        return currency_data_to_send
    else:   
        json_data = await open_json_data('other/other.json', 'r')
        json_data2 = await open_json_data('findata/monthlydata.json', 'r')
        for currency in json_data["currency"]:
            if currency_data in currency["cc"] or currency_data in currency["name"]:
                json_data2['Accounts'][month_year][str(user_id)]['currency'] = currency["symbol"]
                await open_json_data('findata/monthlydata.json', 'w', json_data2)
                return currency["name"], currency['symbol']