import telebot
import requests
import mysql.connector

bot = telebot.TeleBot('6599030364:AAGAtUEZPg0Au8bDr5Psjh9Ro66d7U8lFLk')  # Токен

# Подключение к базе данных MySQL
db_connection = mysql.connector.connect(
    host='localhost',  #  'localhost'
    user='root',  # root
    password='root',  # root
)

cursor = db_connection.cursor()

# Создаем базу данных
create_db_query = "CREATE DATABASE IF NOT EXISTS myfirstdb"
cursor.execute(create_db_query)

# Подключаемся к базе данных myfirstdb 
db_connection.database = 'myfirstdb'

# Создаем таблицу exchange_rates
create_table_query = """
CREATE TABLE IF NOT EXISTS exchange_rates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    currency VARCHAR(3) NOT NULL,
    rate DECIMAL(10, 5) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

cursor.execute(create_table_query)

def get_exchange_rate_from_api(base_currency, target_currency):
    url = f'https://api.exchangerate-api.com/v4/latest/{base_currency}'
    response = requests.get(url)
    data = response.json()
    return data['rates'][target_currency]

def save_exchange_rate(currency, rate):
    insert_query = "INSERT INTO exchange_rates (currency, rate) VALUES (%s, %s) ON DUPLICATE KEY UPDATE rate = %s"
    cursor.execute(insert_query, (currency.upper(), rate, rate))
    db_connection.commit()

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = telebot.types.KeyboardButton('USD')
    itembtn2 = telebot.types.KeyboardButton('EUR')
    markup.add(itembtn1, itembtn2)

    bot.send_message(chat_id=message.chat.id, text="Пожалуйста, выберите валюту:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ['USD', 'EUR'])
def get_exchange_rate(message):
    currency = message.text
    base_currency = 'UAH'  # Гривна

    rate = get_exchange_rate_from_api(currency, base_currency)

    # Сохраняем курс в базе данных
    save_exchange_rate(currency, rate)

    bot.send_message(chat_id=message.chat.id, text=f"<b>Курс {currency.upper()} к {base_currency}: {rate:.5f}</b>", parse_mode="html")

bot.polling(none_stop=True)
