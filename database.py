import sqlite3

database = sqlite3.connect('weather_bot.db')
cursor = database.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS history(
        city_id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id BIGINT,
        city TEXT,
        temp TEXT,
        wind_speed TEXT,
        sunrise TEXT, 
        sunset TEXT
    );
''')

database.commit()
database.close()