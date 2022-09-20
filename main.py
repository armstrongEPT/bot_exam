import bs4
import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types
import csv

CSV_xiaomi = 'xiaomi.csv'
CSV_apple = 'apple.csv'
HOST = 'https://shop.mts.by/'
HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
    }

url1 = 'https://shop.mts.by/phones/Xiaomi/?page=1&num=36'
url2 = 'https://shop.mts.by/phones/Apple/?page=1&num=36'

def get_html(url, params=''):
    r = requests.get(url, headers=HEADERS, params=params)
    return r
def phones(html):
    soup = bs4.BeautifulSoup(html.text, 'html.parser')
    items = soup.find_all('div', class_='products__unit')
    phones = []
    for item in items:
        phones.append(
            {
                'title': item.find('div', class_='products__unit__title').get_text(strip=True),
                'link_title': HOST + item.find('div', class_='products__unit__title').find('a').get('href'),
                'title_info': item.find('div', class_='products__unit__info').get_text(strip=True),
                'title_price': item.find('div', class_='products__unit__price').get_text(strip=True)
            }
        )
    return  phones

def save_phones(items, path):
    with open(path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='|')
        writer.writerow(['name', 'link', 'info', 'price'])
        for item in items:
            writer.writerow(
                [item['title'], item['link_title'], item['title_info'], item['title_price']])

def parser_phones():
    html1 = get_html(url1)
    if html1.status_code == 200:
        xi_phones = []
        for page in range(3):
            html = get_html(url1, params={'page': page})
            xi_phones.extend(phones(html))
            save_phones(xi_phones, CSV_xiaomi)
    html2 = get_html(url2)
    if html2.status_code == 200:
        apple_phones = []
        for page in range(3):
            html = get_html(url2, params={'page': page})
            apple_phones.extend(phones(html))
            save_phones(apple_phones, CSV_apple)

parser_phones()

bot = telebot.TeleBot('5546001741:AAGClEu550ZujOTGuOzUwWQmX6RsWhALNUo')


@bot.message_handler(commands=['start'])
def start(message):
    kb = types.InlineKeyboardMarkup()
    kb_xiaomi = types.InlineKeyboardButton(text='Xiaomi', callback_data='xiaomi')
    kb_apple = types.InlineKeyboardButton(text='Apple', callback_data='apple')
    kb_help = types.InlineKeyboardButton(text='Help', callback_data='help')
    kb.add(kb_xiaomi, kb_apple, kb_help)
    bot.send_message(message.chat.id, f'Привет {message.from_user.first_name} Выбери категорию смартфонов!', reply_markup=kb)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'xiaomi':
        with open('xiaomi.csv', 'r', encoding='utf-8') as file:
            bot.send_message(call.message.chat.id, text='собираю информацию, пожалуйста подождите')
            bot.send_document(call.message.chat.id, file)
    elif call.data == 'apple':
        with open('apple.csv', 'r', encoding='utf-8') as file:
            bot.send_message(call.message.chat.id, text='собираю информацию, пожалуйста подождите')
            bot.send_document(call.message.chat.id, file)
    elif call.data == 'help':
            bot.send_message(call.message.chat.id, text=f'Привет {call.from_user.first_name}, я bot MTS.Shop, в данный момент мы парсим страницы телефонов Xiaomi и Apple')




bot.polling(none_stop=True)
