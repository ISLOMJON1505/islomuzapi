import requests
from bs4 import BeautifulSoup
import sqlite3

# Kirill yozuvdagi hafta kunlarini lotin yozuviga o'girish uchun lug'at
weekday_translation = {
    "Душанба": "Dushanba",
    "Сешанба": "Seshanba",
    "Чоршанба": "Chorshanba",
    "Пайшанба": "Payshanba",
    "Жума": "Juma",
    "Шанба": "Shanba",
    "Якшанба": "Yakshanba"
}

# SQLite bazasini yaratish
conn = sqlite3.connect('namoz_vaqtlari.db')
cursor = conn.cursor()

# Jadvalni yaratish (agar mavjud bo'lmasa)
cursor.execute(''' 
CREATE TABLE IF NOT EXISTS namoz_vaqtlari (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    region TEXT,
    month INTEGER,
    hijriy_day INTEGER,  -- Hijriy kunini integer tipida saqlash
    day INTEGER,
    weekday TEXT,
    sahar TEXT,
    quyosh TEXT,
    peshin TEXT,
    asr TEXT,
    iftor TEXT,
    hufton TEXT
)
''')

# Sessiya yaratish
session = requests.Session()

# Viloyat va oyni foydalanuvchidan olish
region = input("Viloyatni kiriting: ")
month = int(input("Oyni kiriting (1-12 oralig'ida): "))

# Oddiy link
url = 'https://islom.uz/vaqtlar/27/10'  # To'g'ri lotin manzilini o'rnating

# HTML ma'lumotlarini olish
response = session.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Jadval qatorlarini olish
table = soup.find('table', class_='table table-bordered prayer_table')
rows = table.find_all('tr')[1:]  # 0-index qatori header

for row in rows:
    cells = row.find_all('td')
    if cells:  # bo'sh bo'lmasa
        hijriy_day = int(cells[0].text.strip())  # hijriy kunini int tipiga o'zgartirish
        day = int(cells[1].text.strip())  # milodiy oyidagi kun
        weekday_kirill = cells[2].text.strip()  # hafta kuni kirill yozuvda
        weekday = weekday_translation.get(weekday_kirill, weekday_kirill)  # lotinchaga o'girish
        sahar = cells[3].text.strip()  # sahar
        quyosh = cells[4].text.strip()  # quyosh
        peshin = cells[5].text.strip()  # peshin
        asr = cells[6].text.strip()  # asr
        iftor = cells[7].text.strip()  # iftor
        hufton = cells[8].text.strip()  # hufton

        # Ma'lumotlarni bazaga qo'shish
        cursor.execute(''' 
        INSERT INTO namoz_vaqtlari (region, month, hijriy_day, day, weekday, sahar, quyosh, peshin, asr, iftor, hufton)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (region, month, hijriy_day, day, weekday, sahar, quyosh, peshin, asr, iftor, hufton))

# O'zgarishlarni saqlash va bog'lanishni yopish
conn.commit()
conn.close()
