import sqlite3

# Ma'lumotlar bazasini yaratish
conn = sqlite3.connect('namoz_vaqtlari.db')
cursor = conn.cursor()

# Jadvalni yaratish (agar mavjud bo'lmasa)
cursor.execute(''' 
CREATE TABLE IF NOT EXISTS namoz_vaqtlari (
    id INTEGER PRIMARY KEY,
    region TEXT,
    month INTEGER,
    day INTEGER,
    hijri_month TEXT,
    hijri_day INTEGER,
    weekday TEXT,
    sahar TEXT,
    quyosh TEXT,
    peshin TEXT,
    asr TEXT,
    iftor TEXT,
    hufton TEXT
)
''')

# O'zgarishlarni saqlash va bog'lanishni yopish
conn.commit()
conn.close()
