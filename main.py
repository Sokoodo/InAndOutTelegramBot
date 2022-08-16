#!/usr/bin/python

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.
from oauth2client.service_account import ServiceAccountCredentials
# from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import gspread
# import json
import telebot
from datetime import datetime

# from telebot import types

API_TOKEN = 'Your Telebot Token'
bot = telebot.TeleBot(API_TOKEN)
user = bot.get_me()
TelegramUsers = ['Your UserID (INTEGER)']

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scopes)
client = gspread.authorize(credentials)
sheet = client.open("Income and Expense Tracker").sheet1

record_dict = {}
months_dict = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
               "09": "Sept", "10": "Oct", "11": "Nov", "12": "Dec"}


def today_date():
    a = datetime.now()
    a = str(a.strftime('%d/%m/%y'))
    return a


def get_inout(message):
    inout = message.text
    print("In or Out: ", inout)
    record_dict["in or out"] = inout

    if inout.lower() == 'out':
        start_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        start_markup.row('Groceries', 'Restaurants', 'Outs', 'Gifts')
        start_markup.row('Subscriptions', 'HairDresser', 'UniTax', 'Clothing')
        start_markup.row('Travel', 'Transportation', 'Others')
        sent = bot.send_message(message.chat.id, "Choose a category", reply_markup=start_markup)
        print(message.text)
        bot.register_next_step_handler(sent, get_category)
    elif inout.lower() == 'in':
        start_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        start_markup.row('Spotify', 'Erdis', 'Online')
        start_markup.row('Jobs', 'Gifts', 'Others')
        sent = bot.send_message(message.chat.id, "Choose a category", reply_markup=start_markup)
        print(message.text)
        bot.register_next_step_handler(sent, get_category)


def get_category(message):
    category = message.text
    print("Category: ", category)
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
    print("Date: ", datee)
    sent = bot.send_message(message.chat.id, "Amount?")
    bot.register_next_step_handler(sent, get_amt)


def get_amt(message):
    amt = message.text
    record_dict["Amount"] = amt
    print(amt)
    sent = bot.send_message(message.chat.id, "Description?")
    bot.register_next_step_handler(sent, get_description)


def get_description(message):
    desc = message.text
    record_dict["Description"] = desc
    print(desc)
    print(record_dict)
    bot.send_message(message.chat.id, "Updating...")
    update_sheet(message)


# Checks if User is Authorized or not
def UserCheck(message):
    if message.from_user.id in TelegramUsers:
        return True
    else:
        bot.reply_to(message, "Unauthorized User")
        print(message.from_user.id)
        return False


def month_check():
    x = list(record_dict["Date"])
    x = x[-5:-3]
    y = ''.join(x)
    return y


def upload_data(worksheet, cell):
    cell_row = cell.row + 1
    cell_col = cell.col
    cell_val = worksheet.cell(cell_row, cell_col).value
    print(cell_val)
    while cell_val is not None:
        cell_row = cell_row + 1
        print(cell_row)
        cell_val = worksheet.cell(cell_row, cell_col).value
    print("Row {} is None".format(cell_row))
    worksheet.update_cell(cell_row, cell_col, record_dict['Category'])
    worksheet.update_cell(cell_row, cell_col - 1, record_dict['Description'])
    worksheet.update_cell(cell_row, cell_col - 2, record_dict['Amount'])
    worksheet.update_cell(cell_row, cell_col - 3, record_dict['Date'])


def update_sheet(message):
    if (record_dict["in or out"]) == "Out":
        worksheet = sheet.worksheet("Transactions")  # get Transactions worksheet of the Spreadsheet
        cell = worksheet.find("Category out")
        upload_data(worksheet, cell)
        mthcheck = month_check()
        for x in months_dict:
            if x == mthcheck:
                print(months_dict[x])
                worksheet = sheet.worksheet(months_dict[x])
                cell = worksheet.find("Category out")
                upload_data(worksheet, cell)
                print("Data Uploaded to {}".format(months_dict[x]))
                break
            else:
                continue
        bot.send_message(message.chat.id, "Updated")

    elif (record_dict["in or out"]) == "In":
        worksheet = sheet.worksheet("Transactions")  # get Transactions worksheet of the Spreadsheet
        cell = worksheet.find("Category in")
        upload_data(worksheet, cell)
        mthcheck = month_check()
        for x in months_dict:
            if x == mthcheck:
                print(months_dict[x])
                worksheet = sheet.worksheet(months_dict[x])
                cell = worksheet.find("Category in")
                upload_data(worksheet, cell)
                print("Data Uploaded to {}".format(months_dict[x]))
                break
            else:
                continue
        bot.send_message(message.chat.id, "Updated")

    print(record_dict)


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    if UserCheck(message):
        bot.reply_to(message, "Welcome {}".format(message.from_user.first_name) + """\n
        I am here to keep track of your income and expenses. Use the command /add to upload a record!\
        """)
    else:
        pass


@bot.message_handler(commands=['add'])
def add_record(message):
    if UserCheck(message):
        start_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        start_markup.row('In', 'Out')
        sent = bot.send_message(message.chat.id, "Money In or Out? ", reply_markup=start_markup)
        bot.register_next_step_handler(sent, get_inout)
    else:
        pass


# def kill_bot(message):
#     bot.reply_to(message, """\
# See you soon!\
# """)

# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    message.text = message.text.lower()
    if message.text == 'hello':
        bot.reply_to(message, 'Hello, how are you?')
    elif message.text == 'fine':
        bot.reply_to(message, 'Nice, me too!')
    else:
        bot.reply_to(message, 'I don\'t know what to do, send another command please.')


bot.infinity_polling()
