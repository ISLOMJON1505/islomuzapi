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
    id INTEGER PRIMARY KEY,
    viloyat TEXT,
    oy INTEGER,
    milodiy_month INTEGER,
    hijriy_day TEXT,
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

# Lotin tiliga o'tish
lotin_url = 'https://islom.uz/lotin'
session.get(lotin_url)  # Lotin tiliga o'tish

# Keyingi sahifaga o'tish (vaqtlar sahifasi)
url = 'https://islom.uz/vaqtlar/27/10'  # To'g'ri lotin manzilini o'rnating

# HTML ma'lumotlarini olish
response = session.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Viloyat va oyni foydalanuvchidan olish
viloyat = input("Viloyatni kiriting: ")
oy = int(input("Oyni kiriting (1-12 oralig'ida): "))

# Jadval qatorlarini olish
table = soup.find('table', class_='table table-bordered prayer_table')
rows = table.find_all('tr')[1:]  # 0-index qatori header

for row in rows:
    cells = row.find_all('td')
    if cells:  # bo'sh bo'lmasa
        hijriy_day = cells[0].text.strip()  # hijriy kun
        milodiy_month = int(cells[1].text.strip())  # milodiy oyi (son tipida)
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
        INSERT INTO namoz_vaqtlari (viloyat, oy, milodiy_month, hijriy_day, weekday, sahar, quyosh, peshin, asr, iftor, hufton)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (viloyat, oy, milodiy_month, hijriy_day, weekday, sahar, quyosh, peshin, asr, iftor, hufton))

# O'zgarishlarni saqlash va bog'lanishni yopish
conn.commit()
conn.close()
