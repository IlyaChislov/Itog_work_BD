import random

import psycopg2
from telebot import types, TeleBot, custom_filters
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage

import datebase

token_bot = '6898568209:AAFY8eTdxSakbFC-BJSDD6XZeLhmpgLlYVo'
conn = psycopg2.connect(database='english_russian', user='postgres', password='postgres')
data_for_query_new_word = []


def show_target(data):
    return f"{data['target_word']} -> {data['translate_word']}"


def show_hint(*lines):
    return '\n'.join(lines)


class Command:
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово из учебного списка🔙'
    NEXT = 'Дальше ⏭'
    EXIT = 'Завершить обучение'


class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_words = State()


state_storage = StateMemoryStorage()
bot = TeleBot(token_bot, state_storage=state_storage)
print('Start telegram bot...')


@bot.message_handler(commands=['start'])
def start_command(message):
    id_user = message.from_user.id
    if datebase.check_id_user(conn, id_user):
        datebase.insert_user(conn, id_user, message.from_user.username)
        datebase.insert_users_words_start(conn, message.from_user.id)
        bot.send_message(message.chat.id,
                         f"Приветствую, дорогой студент {message.from_user.username}, давай приступим к изучению английского языка")
    markup = types.ReplyKeyboardMarkup(row_width=3)

    global buttons
    buttons = []
    english_words = datebase.select_random_word_for_user(conn, id_user)
    target_word = random.choice(english_words)
    english_words.remove(target_word)
    other_words = english_words
    translate = datebase.translate_word(conn, target_word)
    target_word_btn = types.KeyboardButton(target_word)
    other_words_btns = [types.KeyboardButton(word) for word in random.sample(other_words, 4)]
    buttons.append(target_word_btn)
    buttons.extend(other_words_btns)
    random.shuffle(buttons)
    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    exit_btn = types.KeyboardButton(Command.EXIT)
    buttons.extend([next_btn, add_word_btn, delete_word_btn, exit_btn])
    markup.add(*buttons)
    greeting = f"Выбери перевод слова:\n🇷🇺 {translate}"
    bot.send_message(message.chat.id, greeting, reply_markup=markup)
    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['target_word'] = target_word
        data['translate_word'] = translate
        data['other_words'] = other_words


@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    start_command(message)


@bot.message_handler(func=lambda message: message.text == Command.EXIT)
def exit_education(message):
    bot.send_message(message.chat.id, "Делу время, потехе час! Для возобновления учёбы введите /start")


@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word(message):
    bot.send_message(message.chat.id,
                     "Введите слово на английском для удаления, публичные слова удалять нельзя, только персональные")
    bot.register_next_step_handler(message, del_word)


def del_word(message):
    english_word = message.text.lower()
    id_user = message.from_user.id
    res = datebase.delete_word(conn, id_user, english_word)
    if res == True:
        count = datebase.count_word(conn, id_user)
        bot.send_message(message.chat.id, f"Ваш словарь обновлён, теперь в него входит {count} слов")
        start_command(message)
    else:
        bot.send_message(message.chat.id, "Данного слова нет среди Ваших персональных слов, введите другое слово ")
        delete_word(message)


@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word(message):
    bot.send_message(message.chat.id,
                     "Введите слово на английском языке, которое хотите добавить в словарь")  # сохранить в БД
    bot.register_next_step_handler(message, english_word_input)


def english_word_input(message):
    english_word = message.text.lower()
    id_user = message.from_user.id
    # проверка есть ли данное слово в принципе в БД
    first_check = datebase.check_word_in_bd(conn, english_word)
    if not first_check:
        # такого слова нет в вообще БД (ни у одного из других пользователей в личном словаре, ни среди публичных)
        # поэтому заносим его в БД и потом конкретно в индивидуальный словарь пользователя
        data_for_query_new_word.append(id_user)
        data_for_query_new_word.append(english_word)
        bot.send_message(message.chat.id,
                         "Введите теперь это слово на русском языке")
        bot.register_next_step_handler(message, russian_word_input)
    else:
        # если слово уже есть в БД.
        # проверяем есть ли оно уже в индивидуальном словаре пользователя
        second_check = datebase.check_word_in_users_vocab(conn, first_check, id_user)
        if second_check:
            # У пользователя нет такого слова, добавляем ему
            datebase.insert_id_user_id_word(conn, id_user, english_word)
            count = datebase.count_word(conn, id_user)
            bot.send_message(message.chat.id, f"Ваш словарь обновлён, теперь в него входит {count} слов")
            bot.send_message(message.chat.id, "Продолжим обучение")
            start_command(message)
        else:
            # У пользователя уже есть такое слово в словаре, оповещаем его об этом
            bot.send_message(message.chat.id,
                             "У Вас уже есть такое слово в индивидуальном словаре, введите другое слово")
            add_word(message)


def russian_word_input(message):
    russian_word = message.text.lower()
    data_for_query_new_word.append(russian_word)
    # заносим слово в таблицу слов
    datebase.insert_word(conn, data_for_query_new_word[1], data_for_query_new_word[2], False)
    # заносим слово в словарь конкретного пользователя
    datebase.insert_id_user_id_word(conn, data_for_query_new_word[0], data_for_query_new_word[1])
    count = datebase.count_word(conn, data_for_query_new_word[0])
    bot.send_message(message.chat.id, f"Ваш словарь обновлён, теперь в него входит {count} слов")
    bot.send_message(message.chat.id, "Продолжим обучение")

    start_command(message)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    text = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']
        if text == target_word:
            hint = show_target(data)
            hint_text = ["Отлично!❤", hint]
            next_btn = types.KeyboardButton(Command.NEXT)
            add_word_btn = types.KeyboardButton(Command.ADD_WORD)
            delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
            exit_btn = types.KeyboardButton(Command.EXIT)
            buttons.extend([next_btn, add_word_btn, delete_word_btn, exit_btn])
            hint = show_hint(*hint_text)
        else:
            for btn in buttons:
                if btn.text == text:
                    btn.text = text + '❌'
                    break
            hint = show_hint("Допущена ошибка!",
                             f"Попробуй ещё раз вспомнить слово 🇷🇺{data['translate_word']}")
    markup.add(*buttons)
    bot.send_message(message.chat.id, hint, reply_markup=markup)


bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.polling(skip_pending=True)
