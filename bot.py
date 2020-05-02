import telebot
from telebot import types
import random
import requests
import os
import json

token = os.environ["TELEGRAM_TOKEN"]
bot = telebot.TeleBot(token)
telebot.apihelper.proxy = {'https': 'socks5://stepik.akentev.com:1080'}

scores = {'victories': 0, 'defeats': 0}

MAIN_STATE = 'main'
QUESTION_ASK = 'question'
COMPLEXITY_CHOOSE = 'complexity'

#data = {'states': {}, 'user_complexity':{}, MAIN_STATE:{}, QUESTION_ASK:{}, COMPLEXITY_CHOOSE:{}}

data = json.load(open('db/data.json', 'r', encoding='utf-8'))

def change_data(key, user_id, value):
    data[key][user_id] = value
    json.dump(data,
              open('db/data.json', 'w', encoding='utf-8'),
              indent=2,
              ensure_ascii=False)

keyboard_main = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=False)
keyboard_main.add(types.KeyboardButton('Задай вопрос!'), types.KeyboardButton('Покажи счет.'),
                  types.KeyboardButton('Поменять сложность.'))

@bot.message_handler(func=lambda message: data['states'].get(str(message.from_user.id), MAIN_STATE) == MAIN_STATE)
def main_handler(message):
    comp = data['user_complexity'].get(str(message.from_user.id), 1)
    global QUESTIONS
    QUESTIONS = requests.get('https://stepik.akentev.com/api/millionaire', params={'complexity': comp}).json()
    print(message)
    if message.text == '/start':
        bot.reply_to(message, 'Привет, это бот-игра "Миллионер"!', reply_markup=keyboard_main)
    elif 'задай вопрос!' in message.text.lower():
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
        answers_array = QUESTIONS['answers']
        array = []
        for var in answers_array:
            array.append(types.KeyboardButton(var))
        random.shuffle(array)
        keyboard.add(*array)
        bot.reply_to(message, QUESTIONS['question'], reply_markup=keyboard)
        #data['states'][message.from_user.id] = QUESTION_ASK
        change_data('states', str(message.from_user.id), QUESTION_ASK)
    elif 'покажи счет.' in message.text.lower():
        bot.reply_to(message, 'Побед: ' + str(scores.get('victories')) + ' Поражений: ' + str(scores.get('defeats')))
    elif 'поменять сложность.' in message.text.lower():
        keyboard_complexity = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
        keyboard_complexity.add(types.KeyboardButton('1 сложность'), types.KeyboardButton('2 сложность'),
                                types.KeyboardButton('3 сложность'), types.KeyboardButton('Назад.'))
        bot.reply_to(message, 'Выбери сложность вопросов, сейчас сложность: ' + str(comp),
                     reply_markup=keyboard_complexity)
        #data['states'][message.from_user.id] = COMPLEXITY_CHOOSE
        change_data('states', str(message.from_user.id), COMPLEXITY_CHOOSE)
    else:
        bot.reply_to(message, 'я тебя не понял')


@bot.message_handler(func=lambda message: data['states'].get(str(message.from_user.id), MAIN_STATE) == QUESTION_ASK)
def question_ask(message):
    print(message)
    if message.text == QUESTIONS['answers'][0]:
        bot.reply_to(message, 'Правильно!', reply_markup=keyboard_main)
        scores['victories'] += 1
        #data['states'][message.from_user.id] = MAIN_STATE
        change_data('states', str(message.from_user.id), MAIN_STATE)
    else:
        bot.reply_to(message, 'Неправильно :(', reply_markup=keyboard_main)
        scores['defeats'] += 1
        #data['states'][message.from_user.id] = MAIN_STATE
        change_data('states', str(message.from_user.id), MAIN_STATE)


@bot.message_handler(func=lambda message: data['states'].get(str(message.from_user.id), MAIN_STATE) == COMPLEXITY_CHOOSE)
def complexity(message):
    print(message)
    if message.text == '1 сложность':
        bot.reply_to(message, 'Продолжим с вопросами 1-ой сложности?', reply_markup=keyboard_main)
        #data['user_complexity'][message.from_user.id] = 1
        #data['states'][message.from_user.id] = MAIN_STATE
        change_data('states', str(message.from_user.id), MAIN_STATE)
        change_data('user_complexity', str(message.from_user.id), 1)
    elif message.text == '2 сложность':
        bot.reply_to(message, 'Продолжим с вопросами 2-ой сложности?', reply_markup=keyboard_main)
        #data['user_complexity'][message.from_user.id] = 2
        #data['states'][message.from_user.id] = MAIN_STATE
        change_data('states', str(message.from_user.id), MAIN_STATE)
        change_data('user_complexity', str(message.from_user.id), 2)
    elif message.text == '3 сложность':
        bot.reply_to(message, 'Продолжим с вопросами 3-ей сложности?', reply_markup=keyboard_main)
        #data['user_complexity'][message.from_user.id] = 3
        #data['states'][message.from_user.id] = MAIN_STATE
        change_data('states', str(message.from_user.id), MAIN_STATE)
        change_data('user_complexity', str(message.from_user.id), 3)
    elif message.text == 'Назад.':
        bot.reply_to(message, 'Продолжим с прежней сложностью?', reply_markup=keyboard_main)
        #data['states'][message.from_user.id] = MAIN_STATE
        change_data('states', str(message.from_user.id), MAIN_STATE)


bot.polling()