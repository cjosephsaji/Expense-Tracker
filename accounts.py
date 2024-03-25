import datetime
from authorization import open_json_data


async def add_expense(data, user_id, command_to_split):
    month_year = datetime.datetime.now().strftime("%B %Y")
    data_from_user = data.split(command_to_split)
    data_from_user = data_from_user[-1]
    price = ""
    description = ""
    repeat_monthly = False
    if "repeat" in data_from_user:
        repeat_monthly = True
    for el in data_from_user:
        if el.isnumeric() or el == ".":
            price += el
        elif el.isalpha() or el.isspace():
            description += el
    description = description.replace(' repeat', '')
    json_data_read = await open_json_data('findata/monthlydata.json', 'r')
    if price.strip() == "" or description.strip() == "":
        return False
    else:
        if str(user_id) in json_data_read["Accounts"][month_year]:
            json_data_read["Accounts"][month_year][str(user_id)]["Items"].update({description.strip() : {"price":price.strip(), "repeat_monthly" : repeat_monthly}})
        else:
            json_data_read["Accounts"][month_year][str(user_id)]["Items"] = {description.strip() : {"price":price.strip(), "repeat_monthly" : repeat_monthly}}
        await open_json_data('findata/monthlydata.json', 'w', json_data_read)
        return True


async def remove_expense(user_id, user_option):
    menu = ""
    item_num = ""
    month_year = datetime.datetime.now().strftime("%B %Y")
    if "all" in user_option or "everything" in user_option:
        json_data = await open_json_data('findata/monthlydata.json', 'r')
        json_data["Accounts"][month_year][str(user_id)]["Items"] = {}
        await open_json_data('findata/monthlydata.json', 'w', json_data)
        return True
    else:
        for item in user_option:
            if item.isnumeric():
                item_num += item
        if item_num == "":
            json_data = await open_json_data('findata/monthlydata.json', 'r')
            count = 1
            for each_item in json_data["Accounts"][month_year][str(user_id)]["Items"]:
                menu += f'{count}. {each_item} : {json_data["Accounts"][month_year][str(user_id)]["Items"][each_item]["price"]}\n'
                count += 1
            if menu == "":
                menu = "No Products Added!"
            return menu
        else:
            json_data = await open_json_data('findata/monthlydata.json', 'r')
            product_to_remove = list(json_data["Accounts"][month_year][str(user_id)]["Items"])[int(item_num)-1]
            del json_data["Accounts"][month_year][str(user_id)]["Items"][product_to_remove]
            await open_json_data('findata/monthlydata.json', 'w', json_data)
            return True

async def create_monthly_data():
    json_data = await open_json_data('other/other.json', 'r')
    if json_data['month'].strip() != datetime.datetime.now().strftime("%B"):
        previous_month_all_user_expense = []
        json_data_2 = await open_json_data('findata/monthlydata.json', 'r')
        month_year = datetime.datetime.now().strftime("%B %Y")
        previous_month = json_data['month'] + ' ' + json_data['year']
        for user_data in json_data_2['Accounts'][previous_month]:
            previous_month_all_user_expense.append({user_data: json_data_2['Accounts'][previous_month][user_data]})
            new_month_dict = {user_data : {'currency' : '', 'Items' :{}}}
            for _ in json_data_2['Accounts'][previous_month][user_data]:
                for key,value in json_data_2['Accounts'][previous_month][user_data]['Items'].items():
                    new_month_dict[user_data]['currency'] = json_data_2['Accounts'][previous_month][user_data]['currency']
                    if value["repeat_monthly"]:
                        new_month_dict[user_data]['Items'][key] = value
            json_data_2['Accounts'][month_year] = new_month_dict            
        json_data['month'] = datetime.datetime.now().strftime("%B")
        json_data['year'] = datetime.datetime.now().strftime("%Y")
        await open_json_data('findata/monthlydata.json', 'w', json_data_2)
        await open_json_data('other/other.json', 'w', json_data)
        return previous_month_all_user_expense                      
    else:
        return False


async def custom_report(data, user_id):
    json_data = await open_json_data('findata/monthlydata.json', 'r')
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    year = ''
    flag = 0
    month = ''
    price_total = 0
    for month in months:
        if month.lower() in data.lower():
            flag = 1
            break
    if flag == 0:
        month = datetime.datetime.now().strftime("%B")

    for char in data:
        if char.isnumeric():
            year += char
    if year == '':
        year = datetime.datetime.now().strftime("%Y")
    
    month_year = month.strip() + ' ' + year.strip()
    month_expense = ''
    count = 1
    if month_year not in json_data["Accounts"]:
        return False
    else:
        for expense in json_data["Accounts"][month_year][str(user_id)]["Items"]:
            month_expense += str(count) + '. ' + expense + ' : ' + json_data["Accounts"][month_year][str(user_id)]["Items"][expense]['price'] + json_data["Accounts"][month_year][str(user_id)]["currency"] + '\n'
            price_total += float(json_data["Accounts"][month_year][str(user_id)]["Items"][expense]['price'])
            count += 1
        if month_expense == "":
            month_expense = 'No Products Added!'
        else:
            month_expense += f'\nTotal : {price_total}{json_data["Accounts"][month_year][str(user_id)]["currency"]}'
        return month_expense
