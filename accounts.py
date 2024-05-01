import datetime
from authorization import open_json_data
import re

async def add_expense(data, user_id, command_to_split):
    month_year = datetime.datetime.now().strftime("%B %Y")
    pattern = re.compile(r'\badd\b', re.IGNORECASE)
    data_from_user = pattern.sub("", data).split(",")
    json_data_read = await open_json_data('findata/monthlydata.json', 'r')
    for data_to_enter in data_from_user:
        price = ""
        description = ""
        repeat_monthly = False
        if "repeat" in data_to_enter:
            repeat_monthly = True
        for el in data_to_enter:
            if el.isnumeric():
                price += el
            if el == '.' and price[-1].isnumeric():
                price += el
            elif el in ['+', '-', '*', 'x','X','/','÷']:
                if el == 'x' or el == 'X':
                    price += el.replace(el, '*')
                elif el == '/' or el == '÷':
                    price += el.replace(el, '/')
                else:
                    price += el
            elif el.isalpha() or el.isspace():
                description += el
        description = description.replace(' repeat', '')
        if price.strip() == "" or description.strip() == "":
            return False
        else:
            price = str(eval(price))
            if json_data_read["Accounts"][month_year]:
                json_data_read["Accounts"][month_year][str(user_id)]["Items"].update({description.strip() : {"price":price.strip(), "repeat_monthly" : repeat_monthly}})
            else:
                json_data_read["Accounts"][month_year][str(user_id)]["Items"] = {description.strip() : {"price":price.strip(), "repeat_monthly" : repeat_monthly}}
            await open_json_data('findata/monthlydata.json', 'w', json_data_read)
    price_total = 0
    month_expense = ""
    count = 1
    for expense in json_data_read["Accounts"][month_year][str(user_id)]["Items"]:
        month_expense += str(count) + '. ' + f"`{expense}`" + ' : ' + json_data_read["Accounts"][month_year][str(user_id)]["Items"][expense]['price'] + json_data_read["Accounts"][month_year][str(user_id)]["currency"] + '\n'
        price_total += float(json_data_read["Accounts"][month_year][str(user_id)]["Items"][expense]['price'])
        count += 1
    if month_expense == "":
        month_expense = 'No Products Added!'
    else:
        month_expense += f'\nTotal : {round(price_total,2)}{json_data_read["Accounts"][month_year][str(user_id)]["currency"]}'
    return month_expense


async def remove_expense(user_id, user_option):
    month_year = datetime.datetime.now().strftime("%B %Y")
    json_data = await open_json_data('findata/monthlydata.json', 'r')
    products_not_found = ""
    month_expense = ""
    price_total = 0
    count = 1
    integer_menu_products = []
    if "all" in user_option or "everything" in user_option:
        json_data["Accounts"][month_year][str(user_id)]["Items"] = {}
        await open_json_data('findata/monthlydata.json', 'w', json_data)
        return "Deleted all items"
    else:
        pattern = re.compile(r'\bremove\b', re.IGNORECASE)
        data_from_user = pattern.sub("", user_option).split(",")
        for data_to_remove in data_from_user:
            product_found = 1
            if data_to_remove.strip().isnumeric():
                integer_menu_products.append(data_to_remove.strip())
            else:
                try:
                    for data_to_check in list(json_data["Accounts"][month_year][str(user_id)]["Items"]):
                        if data_to_remove.strip().lower() == data_to_check.lower():
                            del json_data["Accounts"][month_year][str(user_id)]["Items"][data_to_check]
                            await open_json_data('findata/monthlydata.json', 'w', json_data)
                            break
                except KeyError:
                    product_found = 0
                    products_not_found += f"{data_to_remove}\n"

        for integer_product_to_remove in sorted(integer_menu_products,reverse=True):
            try:
                product_to_remove = list(json_data["Accounts"][month_year][str(user_id)]["Items"])[int(integer_product_to_remove)-1]
                del json_data["Accounts"][month_year][str(user_id)]["Items"][product_to_remove]
                await open_json_data('findata/monthlydata.json', 'w', json_data)
            except IndexError:
                product_found = 0
                products_not_found += f"Item number : {data_to_remove.strip()}\n"

        for expense in json_data["Accounts"][month_year][str(user_id)]["Items"]:
            month_expense += str(count) + '. ' + f"`{expense}`" + ' : ' + json_data["Accounts"][month_year][str(user_id)]["Items"][expense]['price'] + json_data["Accounts"][month_year][str(user_id)]["currency"] + '\n'
            price_total += float(json_data["Accounts"][month_year][str(user_id)]["Items"][expense]['price'])
            count += 1
        if month_expense == "":
            month_expense = 'Product list emptied'
        else:
            if product_found == 0:
                month_expense += f"Please double-check if the following items exist in the list and try again : \n`{products_not_found}`"
            else:
                month_expense += f'\nTotal : {round(price_total,2)}{json_data["Accounts"][month_year][str(user_id)]["currency"]}'
        return month_expense


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
    if month_year not in json_data["Accounts"] or str(user_id) not in json_data["Accounts"][month_year]:
        return False
    else:
        for expense in json_data["Accounts"][month_year][str(user_id)]["Items"]:
            month_expense += str(count) + '. ' + f"`{expense}`" + ' : ' + json_data["Accounts"][month_year][str(user_id)]["Items"][expense]['price'] + json_data["Accounts"][month_year][str(user_id)]["currency"] + '\n'
            price_total += float(json_data["Accounts"][month_year][str(user_id)]["Items"][expense]['price'])
            count += 1
        if month_expense == "":
            month_expense = 'No Products Added!'
        else:
            month_expense += f'\nTotal : {round(price_total,2)}{json_data["Accounts"][month_year][str(user_id)]["currency"]}'
        return month_expense
