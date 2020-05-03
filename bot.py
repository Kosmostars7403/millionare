import telebot
from telebot import types
import random
import requests
import os
import json
import redis

token = os.environ["TELEGRAM_TOKEN"]
REDIS_URL = os.environ.get('REDIS_URL')

bot = telebot.TeleBot(token)
telebot.apihelper.proxy = {'https': 'socks5://stepik.akentev.com:1080'}

data = {}
MAIN_STATE = 'main'
QUESTION_ASK = 'question'
COMPLEXITY_CHOOSE = 'complexity'

def save_values(key, value):
    if REDIS_URL:
        redis_db = redis.from_url(REDIS_URL)
        redis_db.set(key, value)
    else:
        data[key] = value

def load_values(key):
    if REDIS_URL:
        redis_db = redis.from_url(REDIS_URL)
        return redis_db.get(key)
    else:
        return data.get(key)

scores = {'victories': 0, 'defeats': 0}

# data = {'states': {}, 'user_complexity':{}, MAIN_STATE:{}, QUESTION_ASK:{}, COMPLEXITY_CHOOSE:{}}

# data = json.load(open('db/data.json', 'r', encoding='utf-8'))

def change_data(key, user_id, value):
    data[key][user_id] = value
    json.dump(data,
              open('db/data.json', 'w', encoding='utf-8'),
              indent=2,
              ensure_ascii=False)


keyboard_main = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=False)
keyboard_main.add(types.KeyboardButton('Задай вопрос!'), types.KeyboardButton('Покажи счет.'),
                  types.KeyboardButton('Поменять сложность.'))


# @bot.message_handler(func=lambda message: data['states'].get(str(message.from_user.id), MAIN_STATE) == MAIN_STATE)
@bot.message_handler(
    func=lambda message: load_values('state: {user_id}'.format(user_id=message.from_user.id)) == MAIN_STATE)
def main_handler(message):
    comp = load_values('complexity: {user_id}'.format(user_id=message.from_user.id), 1)
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
        # data['states'][message.from_user.id] = QUESTION_ASK
        # change_data('states', str(message.from_user.id), QUESTION_ASK)
        save_values('state: {user_id}'.format(user_id=message.from_user.id), QUESTION_ASK)
    elif 'покажи счет.' in message.text.lower():
        bot.reply_to(message, 'Побед: ' + str(scores.get('victories')) + ' Поражений: ' + str(scores.get('defeats')))
    elif 'поменять сложность.' in message.text.lower():
        keyboard_complexity = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
        keyboard_complexity.add(types.KeyboardButton('1 сложность'), types.KeyboardButton('2 сложность'),
                                types.KeyboardButton('3 сложность'), types.KeyboardButton('Назад.'))
        bot.reply_to(message, 'Выбери сложность вопросов, сейчас сложность: ' + str(comp),
                     reply_markup=keyboard_complexity)
        # data['states'][message.from_user.id] = COMPLEXITY_CHOOSE
        # change_data('states', str(message.from_user.id), COMPLEXITY_CHOOSE)
        save_values('state: {user_id}'.format(user_id=message.from_user.id), COMPLEXITY_CHOOSE)
    else:
        bot.reply_to(message, 'я тебя не понял')


@bot.message_handler(func=lambda message: load_values('state: {user_id}'.format(user_id=message.from_user.id)) == QUESTION_ASK)
def question_ask(message):
    print(message)
    if message.text == QUESTIONS['answers'][0]:
        bot.reply_to(message, 'Правильно!', reply_markup=keyboard_main)
        scores['victories'] += 1
        # data['states'][message.from_user.id] = MAIN_STATE
        # change_data('states', str(message.from_user.id), MAIN_STATE)
        save_values('state: {user_id}'.format(user_id=message.from_user.id), MAIN_STATE)
    else:
        bot.reply_to(message, 'Неправильно :(', reply_markup=keyboard_main)
        scores['defeats'] += 1
        # data['states'][message.from_user.id] = MAIN_STATE
        # change_data('states', str(message.from_user.id), MAIN_STATE)
        save_values('state: {user_id}'.format(user_id=message.from_user.id), MAIN_STATE)


@bot.message_handler(func=lambda message: load_values('state: {user_id}'.format(user_id=message.from_user.id)) == COMPLEXITY_CHOOSE)
def complexity(message):
    print(message)
    if message.text == '1 сложность':
        bot.reply_to(message, 'Продолжим с вопросами 1-ой сложности?', reply_markup=keyboard_main)
        # data['user_complexity'][message.from_user.id] = 1
        # data['states'][message.from_user.id] = MAIN_STATE
        # change_data('states', str(message.from_user.id), MAIN_STATE)
        # change_data('user_complexity', str(message.from_user.id), 1)
        save_values('complexity: {user_id}'.format(user_id=message.from_user.id), 1)
        save_values('state: {user_id}'.format(user_id=message.from_user.id), MAIN_STATE)
    elif message.text == '2 сложность':
        bot.reply_to(message, 'Продолжим с вопросами 2-ой сложности?', reply_markup=keyboard_main)
        # data['user_complexity'][message.from_user.id] = 2
        # data['states'][message.from_user.id] = MAIN_STATE
        # change_data('states', str(message.from_user.id), MAIN_STATE)
        # change_data('user_complexity', str(message.from_user.id), 2)
        save_values('complexity: {user_id}'.format(user_id=message.from_user.id), 2)
        save_values('state: {user_id}'.format(user_id=message.from_user.id), MAIN_STATE)
    elif message.text == '3 сложность':
        bot.reply_to(message, 'Продолжим с вопросами 3-ей сложности?', reply_markup=keyboard_main)
        # data['user_complexity'][message.from_user.id] = 3
        # data['states'][message.from_user.id] = MAIN_STATE
        # change_data('states', str(message.from_user.id), MAIN_STATE)
        # change_data('user_complexity', str(message.from_user.id), 3)
        save_values('complexity: {user_id}'.format(user_id=message.from_user.id), 3)
        save_values('state: {user_id}'.format(user_id=message.from_user.id), MAIN_STATE)
    elif message.text == 'Назад.':
        bot.reply_to(message, 'Продолжим с прежней сложностью?', reply_markup=keyboard_main)
        # data['states'][message.from_user.id] = MAIN_STATE
        # change_data('states', str(message.from_user.id), MAIN_STATE)
        save_values('state: {user_id}'.format(user_id=message.from_user.id), MAIN_STATE)

bot.polling()
