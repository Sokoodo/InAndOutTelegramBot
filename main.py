#!/usr/bin/python

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import telebot
from datetime import datetime

API_TOKEN = ''
bot = telebot.TeleBot(API_TOKEN)
user = bot.get_me()
TelegramUsers = []

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scopes)
client = gspread.authorize(credentials)
sheet = client.open("Income and Expense Tracker")

record_dict = {}
months_dict = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
               "09": "Sept", "10": "Oct", "11": "Nov", "12": "Dec"}


def today_date():
    a = datetime.now()
    a = str(a.strftime('%d/%m/%y'))
    return a


def get_inout(message):
    inout = message.text
    record_dict["in or out"] = inout
    if inout.lower() == 'out':
        start_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        start_markup.row('Groceries', 'Restaurants', 'Outs', 'Gifts')
        start_markup.row('Subscriptions', 'HairDresser', 'UniTax', 'Clothing')
        start_markup.row('Travel', 'Transportation', 'Others')
        sent = bot.send_message(message.chat.id, "Choose a category", reply_markup=start_markup)
        bot.register_next_step_handler(sent, get_category)
    elif inout.lower() == 'in':
        start_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        start_markup.row('Spotify', 'Erdis', 'Online')
        start_markup.row('Jobs', 'Gifts', 'Others')
        sent = bot.send_message(message.chat.id, "Choose a category", reply_markup=start_markup)
        bot.register_next_step_handler(sent, get_category)


def get_inout_remove(message):
    inout = message.text
    record_dict["in or out"] = inout
    record_dict["Category"] = ''
    record_dict["Date"] = ''
    record_dict["Amount"] = ''
    record_dict["Description"] = ''
    datee = today_date()
    if inout.lower() == 'out':
        worksheet = sheet.worksheet("Transactions")  # get Transactions worksheet of the Spreadsheet
        cell = worksheet.find("Category out")
        upload_data(worksheet, cell, remove=True)
        record_dict["Date"] = datee  # reset today date just to check the month
        mthcheck = month_check()
        for x in months_dict:
            if x == mthcheck:
                worksheet = sheet.worksheet(months_dict[x])
                cell = worksheet.find("Category out")
                record_dict["Date"] = ''
                upload_data(worksheet, cell, remove=True)
                break
            else:
                continue
    elif inout.lower() == 'in':
        worksheet = sheet.worksheet("Transactions")  # get Transactions worksheet of the Spreadsheet
        cell = worksheet.find("Category in")
        upload_data(worksheet, cell, remove=True)
        record_dict["Date"] = datee  # reset today date just to check the month
        mthcheck = month_check()
        for x in months_dict:
            if x == mthcheck:
                worksheet = sheet.worksheet(months_dict[x])
                cell = worksheet.find("Category in")
                record_dict["Date"] = ''
                upload_data(worksheet, cell, remove=True)
                break
            else:
                continue
    bot.send_message(message.chat.id, "Updated, you can /add another line or /removeLast")


def get_category(message):
    category = message.text
    record_dict["Category"] = category
    start_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    start_markup.row('Today')
    sent = bot.send_message(message.chat.id, "Date? (in dd/mm/yy)", reply_markup=start_markup)
    bot.register_next_step_handler(sent, get_date)


def get_date(message):
    if message.text == 'Today':
        datee = today_date()
        record_dict["Date"] = datee
    else:
        datee = message.text
        record_dict["Date"] = datee
    sent = bot.send_message(message.chat.id, "Amount?")
    bot.register_next_step_handler(sent, get_amt)


def get_amt(message):
    amt = message.text
    record_dict["Amount"] = amt
    sent = bot.send_message(message.chat.id, "Description?")
    bot.register_next_step_handler(sent, get_description)


def get_description(message):
    desc = message.text
    record_dict["Description"] = desc
    bot.send_message(message.chat.id, "Updating...")
    update_sheet(message)


# Checks if User is Authorized or not
def user_check(message):
    if message.from_user.id in TelegramUsers:
        return True
    else:
        bot.reply_to(message, "Unauthorized User")
        return False


def month_check():
    x = list(record_dict["Date"])
    x = x[-5:-3]
    y = ''.join(x)
    return y


def upload_data(worksheet, cell, remove):
    cell_row = cell.row + 1
    cell_col = cell.col
    cell_val = worksheet.cell(cell_row, cell_col).value
    while cell_val is not None:
        cell_row = cell_row + 1
        cell_val = worksheet.cell(cell_row, cell_col).value
    if remove:
        cell_row = cell_row - 1
    worksheet.update_cell(cell_row, cell_col, record_dict['Category'])
    worksheet.update_cell(cell_row, cell_col - 1, record_dict['Description'])
    worksheet.update_cell(cell_row, cell_col - 2, record_dict['Amount'])
    worksheet.update_cell(cell_row, cell_col - 3, record_dict['Date'])


def update_sheet(message):
    if (record_dict["in or out"]) == "Out":
        worksheet = sheet.worksheet("Transactions")  # get Transactions worksheet of the Spreadsheet
        cell = worksheet.find("Category out")
        upload_data(worksheet, cell, remove=False)
        mthcheck = month_check()
        for x in months_dict:
            if x == mthcheck:
                worksheet = sheet.worksheet(months_dict[x])
                cell = worksheet.find("Category out")
                upload_data(worksheet, cell, remove=False)
                break
            else:
                continue
        bot.send_message(message.chat.id, "Updated, you can /add another line or /removeLast")
    elif (record_dict["in or out"]) == "In":
        worksheet = sheet.worksheet("Transactions")  # get Transactions worksheet of the Spreadsheet
        cell = worksheet.find("Category in")
        upload_data(worksheet, cell, remove=False)
        mthcheck = month_check()
        for x in months_dict:
            if x == mthcheck:
                worksheet = sheet.worksheet(months_dict[x])
                cell = worksheet.find("Category in")
                upload_data(worksheet, cell, remove=False)
                break
            else:
                continue
        bot.send_message(message.chat.id, "Updated, you can /add another line or /removeLast")


def get_month_resume(message):
    worksheet = sheet.worksheet(message.text)
    cell_out = worksheet.find("Total Out")
    cell_in = worksheet.find("Total In")
    str_resume = 'MONTH RESUME\n\nTotal Out: \n' + worksheet.cell(cell_out.row + 2,
                                                                  cell_out.col).value + '\n\nTotal In: \n' + worksheet.cell(
        cell_in.row + 2, cell_in.col).value
    bot.reply_to(message, str_resume)


def get_year_resume():
    worksheet = sheet.worksheet('2022 Summary')
    cell_out = worksheet.find("Total Out")
    cell_in = worksheet.find("Total In")
    str_resume = 'YEAR RESUME\n\nTotal Out: \n' + worksheet.cell(cell_out.row + 2,
                                                                 cell_out.col).value + '\n\nTotal In: \n' + worksheet.cell(
        cell_in.row + 2, cell_in.col).value
    return str_resume


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    if user_check(message):
        bot.reply_to(message, "Welcome {}".format(message.from_user.first_name) +
                     "\nI am here to keep track of your income and expenses. Use one of the following commands:\n"
                     "/add to upload a record\n"
                     "/removeLast to remove the last record\n"
                     "/monthResume to see current month resume\n"
                     "/yearResume to see your year resume")
    else:
        pass


@bot.message_handler(commands=['add'])
def add_record(message):
    if user_check(message):
        start_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        start_markup.row('In', 'Out')
        sent = bot.send_message(message.chat.id, "Money In or Out? ", reply_markup=start_markup)
        bot.register_next_step_handler(sent, get_inout)
    else:
        pass


@bot.message_handler(commands=['removeLast'])
def remove_last_line(message):
    if user_check(message):
        start_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        start_markup.row('In', 'Out')
        sent = bot.send_message(message.chat.id, "Remove last In or last Out? ", reply_markup=start_markup)
        bot.register_next_step_handler(sent, get_inout_remove)
    else:
        pass


@bot.message_handler(commands=['monthResume'])
def check_month_resume(message):
    if user_check(message):
        start_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        start_markup.row('Jan', 'Feb', 'Mar', 'Apr')
        start_markup.row('May', 'Jun', 'Jul', 'Aug')
        start_markup.row('Sept', 'Oct', 'Nov', 'Dec')
        sent = bot.send_message(message.chat.id, "Choose a category", reply_markup=start_markup)
        bot.register_next_step_handler(sent, get_month_resume)
    else:
        pass


@bot.message_handler(commands=['yearResume'])
def check_year_resume(message):
    if user_check(message):
        total_year = get_year_resume()
        bot.reply_to(message, total_year)
    else:
        pass


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    message.text = message.text.lower()
    if message.text == 'hello':
        bot.reply_to(message, 'Hello, how are you?')
    elif message.text == 'fine':
        bot.reply_to(message, 'Nice, me too!')
    else:
        bot.reply_to(message, 'I don\'t know what to do, try with /help or /add.')


bot.infinity_polling()
