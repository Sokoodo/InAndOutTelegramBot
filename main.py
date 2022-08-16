#!/usr/bin/python

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.

import telebot
from telebot import types

API_TOKEN = '5553891118:AAGaV6wLx6JmPQmh7q9oi62bMj3d3EbM0Ek'

bot = telebot.TeleBot(API_TOKEN)
user = bot.get_me()


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """\
Hi there, I am your Finance bot.
I am here to keep track of your income and expenses. Send me your money movements!\
""")


@bot.message_handler(commands=['Categories'])
def kill_bot(message):
    markup = types.ReplyKeyboardMarkup()
    add_expense = types.KeyboardButton('add_expense')
    add_income = types.KeyboardButton('add_income')
    c = types.KeyboardButton('c')
    d = types.KeyboardButton('d')
    e = types.KeyboardButton('e')
    markup.row(add_expense, add_income)
    markup.row(c, d, e)
    bot.reply_to(message, "Choose one letter:", reply_markup=markup)


# def kill_bot(message):
#     bot.reply_to(message, """\
# See you soon!\
# """)

# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    if message.text == 'Hello':
        bot.reply_to(message, 'Hello, how are you?')
    elif message.text == 'Fine':
        bot.reply_to(message, 'Nice, me too!')
    else:
        bot.reply_to(message, 'I don\'t know what to do, send another command please.')


bot.infinity_polling()
