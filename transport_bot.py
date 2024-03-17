import telebot
from telebot import types
from telebot.util import async_dec
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
import re
import logging
import os


logger = telebot.logger
telebot.logger.setLevel(logging.ERROR)


class ExceptionHandler(telebot.ExceptionHandler):
    def handle(self, exception):
        logger.error(exception)


path = "secrets\\secret_tocken.txt"
with open(path, "r", encoding='utf-8') as file:
    src = file.read()

bot = telebot.TeleBot(f'{src}', exception_handler=ExceptionHandler(),
                      threaded=True, num_threads=4)

stop_regexp = r'^https:\/\/yandex\.ru\/maps\/-\/[A-Za-z0-9]+'

# Приветственное сообщение


@bot.message_handler(commands=['start'])
def start(message):
    path = f'src\\files\\{message.chat.id}_stops.html'
    open(path, encoding='utf-8', mode='a')

    keysmarkup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    tutorial = types.KeyboardButton(text='Туториал')
    show_stops = types.KeyboardButton(text='Посмотреть остановки')
    add_stop = types.KeyboardButton(text='Добавить остановку')
    delete_stop = types.KeyboardButton(text='Удалить остановку')
    keysmarkup.add(tutorial, show_stops, add_stop, delete_stop)

    bot.send_message(
        message.chat.id, 'Привет! Я - бот, который узнаёт время прибытия транспорта до остановки', reply_markup=keysmarkup)

# Туториал


@bot.message_handler(regexp=r'Туториал')
def send_tutorial(message):
    bot.send_message(message.chat.id, 'Нажав на кнопку "Добавить остановку" вы перейдёте в диалог добавления остановки. Сначала вас попросят прислать ссылку следующего формата: https://yandex.ru/maps/-/CCUrV4w63B, а потом дать остановке название\n\nЧтобы узнать подходящий транспорт нажмите на "Посмотреть остановки" и выберите нужную\n\nЧтобы удалить остановку нажмите на кнопку "Удалить остановку" и выберите ту что хотите удалить.\n\nЕсли у вас пропали кнопки меню, напишите /menu в чат, и они вернуться')

# Меню сгенерировать


@bot.message_handler(commands=['menu'])
def start(message):
    path = f'src\\files\\{message.chat.id}_stops.html'
    open(path, encoding='utf-8', mode='a')

    keysmarkup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    tutorial = types.KeyboardButton(text='Туториал')
    show_stops = types.KeyboardButton(text='Посмотреть остановки')
    add_stop = types.KeyboardButton(text='Добавить остановку')
    delete_stop = types.KeyboardButton(text='Удалить остановку')
    keysmarkup.add(tutorial, show_stops, add_stop, delete_stop)

# Добавление остановки


@bot.message_handler(regexp=r'Добавить остановку')
def add_stop_link(message):
    sent = bot.reply_to(message, 'Пришлите ссылку на остановку с Яндекс карт')
    bot.register_next_step_handler(sent, review_link)


def review_link(message):
    link_to_save = message.text
    print(link_to_save)
    if re.match(stop_regexp, link_to_save) and not is_in_list(link_to_save, message.chat.id):
        path = f'src\\files\\{message.chat.id}_stops.html'
        with open(path, encoding='utf-8', mode='a') as file:
            file.write(link_to_save)
        sent = bot.reply_to(message, 'Назовите эту остановку')
        bot.register_next_step_handler(sent, review_name)
    elif not re.match(stop_regexp, link_to_save):
        bot.reply_to(
            message, 'Ссылка неправильная, она должна быть следующего формата: https://yandex.ru/maps/-/CCUrV4w63B')
    else:
        bot.reply_to(message, 'Эта остановка уже добавлена')


def is_in_list(link_to_save, chat_id):
    path = f'src\\files\\{chat_id}_stops.html'
    with open(path, "r", encoding='utf-8') as file:
        src = file.read()
    result = src.find(link_to_save)

    if result == -1:
        return False
    return True


def review_name(message):
    name_to_save = message.text
    print(name_to_save)
    path = f'src\\files\\{message.chat.id}_stops.html'
    with open(path, encoding='utf-8', mode='a') as file:
        file.write(f', {name_to_save}\n')
    bot.reply_to(message, 'Остановка добавлена')

# Посмотреть список остановок


@bot.message_handler(regexp=r'Посмотреть остановки')
def show_stops(message):
    keyboard = types.InlineKeyboardMarkup()
    path = f'src\\files\\{message.chat.id}_stops.html'
    with open(path, encoding='utf-8', mode='a') as f:
        pass
    with open(path, encoding='utf-8', mode='r') as f:
        for line in f:
            info = line.partition(',')
            link = info[0]
            name = info[2]
            button = types.InlineKeyboardButton(text=f'{name}', callback_data=f'{link}')
            keyboard.add(button)
    bot.send_message(message.chat.id, 'Ваши остановки:', reply_markup=keyboard)

# Удалить остановоку


@bot.message_handler(regexp=r'Удалить остановку')
def delete_stop_link(message):
    deleting_keyboard = types.InlineKeyboardMarkup()
    path = f'src\\files\\{message.chat.id}_stops.html'
    with open(path, encoding='utf-8', mode='r') as f:
        for line in f:
            info = line.partition(',')
            link = info[0]  # удалять по ссылке
            name = info[2]
            button = types.InlineKeyboardButton(text=f'{name}', callback_data=f'delete{link}')
            deleting_keyboard.add(button)
    bot.send_message(message.chat.id, 'Выберите какую остановку удалить:',
                     reply_markup=deleting_keyboard)


def delete_stop(callback, chat_id):
    path = f'src\\files\\{chat_id}_stops.html'

    with open(path, encoding='utf-8', mode='r') as file:
        link_to_delete = callback.partition(',')[0]
        link_to_delete = link_to_delete[6:]
        lines = file.readlines()
        line_number = 0
        for line in lines:
            link = line.partition(',')[0]
            if link == link_to_delete:
                lines.pop(line_number)
                break
            else:
                line_number += 1

    with open(path, encoding='utf-8', mode='w') as file:
        file.writelines(lines)

# Обработчик колбэко


@bot.callback_query_handler(func=lambda callback: callback.data)
def check_callback_data(callback):
    # Добавление остановки
    if re.match(stop_regexp, callback.data):
        get_source_html(callback.data, callback.message.chat.id)
        output = get_stop_info(callback.data, callback.message.chat.id)
        bot.send_message(callback.message.chat.id, {output})
    # Удаление остановки
    else:
        delete_stop(callback.data, callback.message.chat.id)
        bot.send_message(callback.message.chat.id, "Остановка удалена")
        deleting_keyboard = types.InlineKeyboardMarkup()
        path = f'src\\files\\{callback.message.chat.id}_stops.html'
        with open(path, encoding='utf-8', mode='r') as f:
            for line in f:
                info = line.partition(',')
                link = info[0]
                name = info[2]
                button = types.InlineKeyboardButton(text=f'{name}', callback_data=f'delete{link}')
                deleting_keyboard.add(button)
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id,
                              text='Выберите какую остановку удалить:', reply_markup=deleting_keyboard)


def get_stop_info(url, chat_id) -> str:
    uniquename = url.split("/")[-1]

    path = f'src\\files\\{chat_id}_{uniquename}.html'
    with open(path, encoding='utf-8', mode='r') as file:
        # doc = BeautifulSoup(file, "lxml") # для использования lxml нужно докачивать lxml отдельно (pip install lxml)
        doc = BeautifulSoup(file, "html.parser")

    transportTypes = doc.find_all(class_="masstransit-transport-list-view__type-name")

    outputlist = []
    title = doc.title.text
    if len(transportTypes) == 0:
        outputlist.append(
            f'{title} - не имеет информации о прибывающем транспорте\n Скорее всего вы предоставили неправильную ссылку.')
        output = ''.join(outputlist)
        return output

    outputlist.append(title + "\n")
    for i in transportTypes:
        match i.text:
            case "Автобусы":
                findTransportTime(i.text, '_type_bus', outputlist, doc)
            case "Трамваи":
                findTransportTime(i.text, '_type_tramway', outputlist, doc)
            case "Троллейбусы":
                findTransportTime(i.text, '_type_trolleybus', outputlist, doc)
            case "Маршрутки":
                findTransportTime(i.text, '_type_minibus', outputlist, doc)
            case "Электрички":
                findTransportTime(i.text, '_type_suburban', outputlist, doc)
            case _:
                outputlist.append(f'Мы ещё не поддерживаем {i.text}')

    output = ''.join(outputlist)

    os.remove(path)
    return output


def findTransportTime(TransportType, TransportPostfix, outputlist, doc):
    outputlist.append(f"{TransportType}:" + "\n")
    list = doc.find('ul', class_="masstransit-brief-schedule-view__vehicles").find_all('li',
                                                                                       class_=f'{TransportPostfix}')
    for item in list:
        outputlist.append(item.get_text(strip=True, separator=' ') + "\n")
    outputlist.append("\n")


def get_source_html(url, chat_id):
    # driver_service = Service("chromedriver-win64\chromedriver.exe")
    driver_service = Service("chromedriver-linux64\chromedriver")
    driver = webdriver.Chrome(service=driver_service)

    driver.maximize_window()
    try:
        driver.get(url=url)
        time.sleep(1)

        uniquename = url.split("/")[-1]
        while True:
            path = f'src\\files\\{chat_id}_{uniquename}.html'
            with open(path, "w", encoding='utf-8') as file:
                file.write(driver.page_source)
            time.sleep(1)
            break
    except Exception as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()


bot.polling()
