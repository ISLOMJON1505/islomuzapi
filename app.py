from fastapi import FastAPI, HTTPException
import sqlite3
from pydantic import BaseModel
from datetime import datetime, timedelta

app = FastAPI()

# Ma'lumotlar modelini yaratamiz
class HijriDate(BaseModel):
    month: str
    day: int

class Times(BaseModel):
    tong_saharlik: str
    quyosh: str
    peshin: str
    asr: str
    shom_iftor: str
    hufton: str

class DailyPrayerTimeResponse(BaseModel):
    region: str
    regionNumber: int
    month: int
    day: int
    date: str
    hijri_date: HijriDate
    weekday: str
    times: Times

class MonthlyPrayerTimeResponse(BaseModel):
    region: str
    month: int
    prayer_times: list[DailyPrayerTimeResponse]  # Oylik namoz vaqtlarining ro'yxati

class WeeklyPrayerTimeResponse(BaseModel):
    region: str
    week: list[DailyPrayerTimeResponse]  # Haftalik namoz vaqtlarining ro'yxati

# SQLite bazasidan ma'lumot olish funksiyalari
def get_prayer_times(region: str, month: int, day: int):
    conn = sqlite3.connect('namoz_vaqtlari.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM namoz_vaqtlari WHERE region=? AND month=? AND day=?", (region, month, day))
    row = cursor.fetchone()
    conn.close()
    return row

def get_monthly_prayer_times(region: str, month: int):
    conn = sqlite3.connect('namoz_vaqtlari.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM namoz_vaqtlari WHERE region=? AND month=?", (region, month))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_weekly_prayer_times(region: str):
    today = datetime.utcnow()
    week_days = [(today + timedelta(days=i)).day for i in range(7)]  # Joriy haftada kunlar
    month = today.month
    weekly_data = []
    
    for day in week_days:
        row = get_prayer_times(region, month, day)
        if row:
            hijri_date_month = "rabi'us soni"  # Faqat namunaviy hijriy sanani yozish
            hijri_date_day = row[3]  # hijriy kuni
            weekday = today.strftime("%A")  # Haftaning kunini olish
            date_str = datetime.utcnow().isoformat() + "Z"  # ISO formatida sanani olish
            
            weekly_data.append({
                "region": row[1],
                "regionNumber": 27,  # To'g'ri raqamni kiritish
                "month": month,
                "day": day,
                "date": date_str,
                "hijri_date": {"month": hijri_date_month, "day": hijri_date_day},
                "weekday": weekday,
                "times": {
                    "tong_saharlik": row[5],
                    "quyosh": row[6],
                    "peshin": row[7],
                    "asr": row[8],
                    "shom_iftor": row[9],
                    "hufton": row[10],
                }
            })
    return weekly_data

@app.get("/api/present/day", response_model=DailyPrayerTimeResponse)
async def present_daily_prayer_time(region: str):
    today = datetime.utcnow()  # Joriy sanani olish
    month = today.month
    day = today.day
    date_str = today.isoformat() + "Z"  # ISO formatida sanani olish

    row = get_prayer_times(region, month, day)
    if row:
        hijri_date_month = "rabi'us soni"  # Faqat namunaviy hijriy sanani yozish
        hijri_date_day = row[3]  # hijriy kuni
        weekday = today.strftime("%A")  # Haftaning kunini olish

        return {
            "region": row[1],
            "regionNumber": 27,  # To'g'ri raqamni kiritish
            "month": month,
            "day": day,  # Joriy milodiy kunini olish
            "date": date_str,
            "hijri_date": {"month": hijri_date_month, "day": hijri_date_day},
            "weekday": weekday,
            "times": {
                "tong_saharlik": row[5],
                "quyosh": row[6],
                "peshin": row[7],
                "asr": row[8],
                "shom_iftor": row[9],
                "hufton": row[10],
            }
        }
    else:
        raise HTTPException(status_code=404, detail="Namoz vaqtlarini topilmadi")

@app.get("/api/daily", response_model=DailyPrayerTimeResponse)
async def daily_prayer_time(region: str, month: int, day: int):
    row = get_prayer_times(region, month, day)
    if row:
        hijri_date_month = "rabi'us soni"  # Faqat namunaviy hijriy sanani yozish
        hijri_date_day = row[3]  # hijriy kuni
        weekday = datetime.utcnow().strftime("%A")  # Haftaning kunini olish

        return {
            "region": row[1],
            "regionNumber": 27,  # To'g'ri raqamni kiritish
            "month": month,
            "day": day,  # Berilgan milodiy kunini olish
            "date": datetime.utcnow().isoformat() + "Z",  # ISO formatida sanani olish
            "hijri_date": {"month": hijri_date_month, "day": hijri_date_day},
            "weekday": weekday,
            "times": {
                "tong_saharlik": row[5],
                "quyosh": row[6],
                "peshin": row[7],
                "asr": row[8],
                "shom_iftor": row[9],
                "hufton": row[10],
            }
        }
    else:
        raise HTTPException(status_code=404, detail="Namoz vaqtlarini topilmadi")

@app.get("/api/monthly", response_model=MonthlyPrayerTimeResponse)
async def monthly_prayer_time(region: str, month: int):
    rows = get_monthly_prayer_times(region, month)
    if rows:
        prayer_times = []
        for row in rows:
            hijri_date_month = "rabi'us soni"  # Faqat namunaviy hijriy sanani yozish
            hijri_date_day = row[3]  # hijriy kuni
            weekday = datetime.utcnow().strftime("%A")  # Haftaning kunini olish
            date_str = datetime.utcnow().isoformat() + "Z"  # ISO formatida sanani olish
            
            prayer_times.append({
                "region": row[1],
                "regionNumber": 27,  # To'g'ri raqamni kiritish
                "month": month,
                "day": row[4],  # Milodiy kuni
                "date": date_str,
                "hijri_date": {"month": hijri_date_month, "day": hijri_date_day},
                "weekday": weekday,
                "times": {
                    "tong_saharlik": row[5],
                    "quyosh": row[6],
                    "peshin": row[7],
                    "asr": row[8],
                    "shom_iftor": row[9],
                    "hufton": row[10],
                }
            })
        
        return {
            "region": region,
            "month": month,
            "prayer_times": prayer_times
        }
    else:
        raise HTTPException(status_code=404, detail="Namoz vaqtlarini topilmadi")

@app.get("/api/present/week", response_model=WeeklyPrayerTimeResponse)
async def present_weekly_prayer_time(region: str):
    weekly_data = get_weekly_prayer_times(region)
    if weekly_data:
        return {
            "region": region,
            "week": weekly_data
        }
    else:
        raise HTTPException(status_code=404, detail="Namoz vaqtlarini topilmadi")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
