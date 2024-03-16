from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
from telebot import formatting
from telebot.util import quick_markup
import os
import asyncio
import datetime
from time import sleep
from accounts import add_expense, remove_expense, custom_report, create_monthly_data
from authorization import check_auth_user, confirm_request_auth, create_auth_user, check_banned_users, open_json_data, currency
from threading import Thread

load_dotenv()


#admin_id = TELEGRAM_USER_ID
bot = AsyncTeleBot(os.environ.get("TELEGRAM_API"))
menu_markup = quick_markup({
    'Add Product': {'callback_data': 'add'},
    'Remove Product': {'callback_data': 'remove'},
    'Month Report': {'callback_data': 'custom_report'},
}, row_width=2)


async def check_text_command(data):
    command = ''
    json_data = await open_json_data('commanddata/commands.json', 'r')
    for key,value in json_data.items():
        if key in data.lower():
            command =  {key : value}
            break
        else:
            command = False
    return command

@bot.message_handler(func=lambda message: not message.text.startswith('/'))
async def menu_auth(message):
    if await check_banned_users(message.from_user.username) == False:
        if await check_auth_user(message.from_user.id):
                command = await check_text_command(message.text)
                if not command:
                    await bot.reply_to(message,formatting.hcode('Please select anyone') ,reply_markup=menu_markup, parse_mode='HTML')
                else:
                    command_dict = list(command.items())
                    if command_dict[0][1] == 'add':
                        if await currency(message.from_user.id):
                            command = await add_expense(message.text, message.from_user.id, command_dict[0][0])
                            if not command:
                                await bot.reply_to(message,formatting.hcode('Please enter a valid product name and price'), parse_mode='HTML')
                            else:
                                await bot.reply_to(message,formatting.hcode('Done'), parse_mode='HTML')
                        else:
                            await bot.reply_to(message,await currency(message.from_user.id, "setting"),parse_mode='Markdown')
                    elif command_dict[0][1] == 'remove':
                        if await currency(message.from_user.id):
                            response = await remove_expense(message.from_user.id, message.text)
                            if response == True:
                                await bot.reply_to(message,formatting.hcode('Done'), parse_mode='HTML')
                            else:
                                await bot.reply_to(message,formatting.hcode(response), parse_mode='HTML')
                        else:
                            await bot.reply_to(message,await currency(message.from_user.id, "setting"),parse_mode='Markdown')
                    elif command_dict[0][1] == 'custom_report':
                        if await currency(message.from_user.id):
                            response = await custom_report(message.text, message.from_user.id)
                            if not response:
                                await bot.reply_to(message,formatting.hcode(f'Data not Available\nReport available from March 2024 Only\n\nDate Today : {datetime.datetime.now().strftime("%d/%m/%Y")}'), parse_mode='HTML')
                            else:
                                await bot.reply_to(message,formatting.hcode(response), parse_mode='HTML')
                        else:
                            await bot.reply_to(message,await currency(message.from_user.id, "setting"),parse_mode='Markdown')
                    elif command_dict[0][1] == 'currency':
                        currency_data = message.text.replace('currency','')
                        currency_data = await currency(message.from_user.id, currency_data.strip())
                        await bot.reply_to(message,formatting.hcode(f'Your currency has been set to {currency_data[0]} ({currency_data[1]})'),reply_markup=menu_markup, parse_mode='HTML')
                    else:
                        await bot.reply_to(message,formatting.hcode('Please select any one'),reply_markup=menu_markup, parse_mode='HTML')
        else:
            await bot.reply_to(message,formatting.hcode(f"Hello {message.from_user.first_name},\nYou're not an authorized user!\nShall I send a request to the admin for access?"), reply_markup=await confirm_request_auth(), parse_mode='HTML')
    else:
        await bot.reply_to(message,formatting.hcode('Sorry you are banned ❌'), parse_mode='HTML')

@bot.message_handler(commands=['start'])
async def start_command(message):
    await menu_auth(message)

@bot.message_handler(commands=['remove'])
async def remove_user(message):
    if message.from_user.id == admin_id:
        await create_auth_user(str(message.text), 'remove_user')
        await bot.reply_to(message,formatting.hcode('Done'), parse_mode='HTML')
    else:
        pass

@bot.message_handler(commands=['ban'])
async def remove_user(message):
    if message.from_user.id == admin_id:
        await create_auth_user(str(message.text), 'ban_user')
        await bot.reply_to(message,formatting.hcode('Done'), parse_mode='HTML')
    else:
        pass

@bot.message_handler(commands=['unban'])
async def remove_user(message):
    if message.from_user.id == admin_id:
        await create_auth_user(str(message.text), 'unban_user')
        await bot.reply_to(message,formatting.hcode('Done'), parse_mode='HTML')
    else:
        pass               

async def start_month_reporter():
    while True:
        response = await create_monthly_data()
        total_price = 0
        if response:
            for each_user_data in response:
                expense = 'Your Previous Month Report\n\n'
                for key, value in each_user_data.items():
                    user_id = key
                    for item, price in value["Items"].items(): 
                        expense += f'{item} : {price["price"]}{value["currency"]}\n'
                        total_price += int(price["price"])
                expense += f'\n\nTotal Expense : {total_price}{value["currency"]}'
                await bot.send_message(user_id, formatting.hcode(expense), parse_mode='HTML')
        await asyncio.sleep(86400)

@bot.message_handler(commands=['startmonthlyreport'])
async def start_month_reporter_command(message):
    if message.from_user.id == admin_id:
        if 'month_report_task' not in globals():
            global month_report_task
            month_report_task = asyncio.create_task(start_month_reporter())
            await bot.reply_to(message, formatting.hcode('Monthly report task started.'), parse_mode='HTML')
        else:
            await bot.reply_to(message, formatting.hcode('A process is already running.'), parse_mode='HTML')
    else:
        pass


@bot.message_handler(commands=['echo'])
async def echo_users(message):
    message_data = message.text.split('/echo')
    json_data = await open_json_data('authdata/authorized_users.json', 'r')
    for item in json_data:
        await bot.send_message(item, message_data[-1])


@bot.callback_query_handler(func=lambda call:True)
async def callback_data(callback):
    if callback.data == 'request_auth_y':
        await create_auth_user(callback, 'awaiting_entry')
        await bot.send_message(admin_id, f'Request from @{callback.from_user.username}', reply_markup=await create_auth_user(callback,'admit_request'), parse_mode='HTML')
        await bot.edit_message_text(formatting.hcode('Your request has been sent to @cjosephsaji ✅'),callback.from_user.id, callback.message.message_id, parse_mode='HTML')
    elif callback.data == 'request_auth_n':
        await bot.edit_message_text(formatting.hcode("Okay 👍"),callback.from_user.id, callback.message.message_id,parse_mode='HTML')
    elif 'confirm_auth_y' in callback.data:
        new_user_details = callback.data
        new_user_id = new_user_details.split('_')
        newuser_name = callback.message.text.split('@')
        await create_auth_user({new_user_id[-1]: newuser_name[-1]}, 'user_admitted')
        await bot.edit_message_text(f'Added User (@{newuser_name[-1]}) ✅',callback.from_user.id, callback.message.message_id)
        await bot.send_message(new_user_id[-1], formatting.hcode("You've been admitted by the admin ✅\n\nHere are your options"), reply_markup=menu_markup, parse_mode='HTML')
    elif 'reject_auth_n' in callback.data:
        new_user_details = callback.data
        new_user_id = new_user_details.split('_')
        newuser_name = callback.message.text.split('@')
        await create_auth_user(new_user_id[-1], 'user_rejected')
        await bot.edit_message_text(f'Rejected User (@{newuser_name[-1]}) ❌',callback.from_user.id, callback.message.message_id)
        await bot.send_message(new_user_id[-1], "`Sorry, you've been rejected ❌`", parse_mode='HTML')
    elif 'add' in callback.data:
        await bot.send_message(callback.from_user.id, "Please use the command below (Click to Copy)\n`add [item name] [price]`\n\n‼️ Don't use the Square Braces\nExample : `add tomato 45`", parse_mode='Markdown')
    elif 'remove' in callback.data:
        await bot.send_message(callback.from_user.id, "Please use the command below (Click to Copy)\n`remove [item number]`\n\n‼️ Don't use the Square Braces\nExample : `remove 1`", parse_mode='Markdown')
    elif 'custom_report' in callback.data:
        await bot.send_message(callback.from_user.id, "Please use the command below (Click to Copy)\n`report [month (optional)] [year (optional)]`\n\n‼️ Don't use the Square Braces\nExample : `report march 2024`", parse_mode='Markdown')
        

asyncio.run(bot.infinity_polling())
