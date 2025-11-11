import telebot
import sqlite3
from datetime import date, datetime

TOKEN = "8435730379:AAHgSq9OPPkIX_-KiffBkoxM75RnOiUks0w"

bot = telebot.TeleBot(TOKEN)
DB_PATH = "school_bot.db"
ADMIN_PASSWORD = "1234"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS homework(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   date TEXT,
                   subject TEXT,
                   text TEXT
                 )""")
    c.execute("""CREATE TABLE IF NOT EXISTS schedule(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   weekday TEXT,
                   period INTEGER,
                   subject TEXT
                 )""")
    conn.commit()
    conn.close()

def add_schedule(weekday, period, subject):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO schedule(weekday,period,subject) VALUES (?,?,?)",(weekday,period,subject))
    conn.commit()
    conn.close()

def get_schedule(weekday):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT period, subject FROM schedule WHERE weekday=? ORDER BY period",(weekday,))
    rows = c.fetchall()
    conn.close()
    return rows

def add_homework(hw_date, subject, text):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO homework(date,subject,text) VALUES (?,?,?)",(hw_date,subject,text))
    conn.commit()
    conn.close()

def get_homework(hw_date):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT subject,text FROM homework WHERE date=?",(hw_date,))
    rows = c.fetchall()
    conn.close()
    return rows

def seed_schedule():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM schedule")
    if c.fetchone()[0] == 0:
        add_schedule("Дүйсенбі",1,"Тәрбие сағаты")
        add_schedule("Дүйсенбі",2,"Ағылшын")
        add_schedule("Дүйсенбі",3,"Қазақ тілі")
        add_schedule("Дүйсенбі",4,"Математика")
        add_schedule("Дүйсенбі",5,"Орыс тілі")
        add_schedule("Сейсенбі",1,"Математика")
        add_schedule("Сейсенбі",2,"Қазақ тілі")
        add_schedule("Сейсенбі",3,"Қазақстан тарихы")
    conn.close()

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
        "Сәлем 👋\nМен оқу көмекшісі ботпын 🤖\n\n"
        "Командалар:\n"
        "📘 /keste – сабақ кестесі\n"
        "📚 /uytap – бүгінгі үй тапсырмасы\n"
        "➕ /addhw – мұғалімге тапсырма қосу")

@bot.message_handler(commands=['keste'])
def show_schedule(message):
    weekdays = {
        'Monday': 'Дүйсенбі', 'Tuesday': 'Сейсенбі', 'Wednesday': 'Сәрсенбі',
        'Thursday': 'Бейсенбі', 'Friday': 'Жұма'
    }
    day = weekdays[datetime.today().strftime("%A")]
    rows = get_schedule(day)
    if not rows:
        bot.send_message(message.chat.id, f"{day} күніне кесте табылмады 😔")
        return
    text = f"📘 {day} күні сабақтар:\n"
    for period, subj in rows:
        text += f"{period}. {subj}\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['uytap'])
def show_homework(message):
    today = date.today().isoformat()
    rows = get_homework(today)
    if not rows:
        bot.send_message(message.chat.id, "📚 Бүгінге үй тапсырмасы жоқ.")
        return
    text = "📘 Бүгінгі үй тапсырмасы:\n"
    for subj, txt in rows:
        text += f"• {subj}: {txt}\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['addhw'])
def add_hw(message):
    try:
        _, password, hw_date, subject, text_hw = message.text.split('|')
        password = password.strip()
        hw_date = hw_date.strip()
        subject = subject.strip()
        text_hw = text_hw.strip()
    except:
        bot.send_message(message.chat.id, "❌ Қате формат!\nМысалы:\n/addhw | 1234 | 2025-11-15 | Математика | 25-жаттығу")
        return

    if password != ADMIN_PASSWORD:
        bot.send_message(message.chat.id, "🚫 Қате пароль.")
        return

    add_homework(hw_date, subject, text_hw)
    bot.send_message(message.chat.id, "✅ Үй тапсырмасы сәтті қосылды!")

if __name__ == "_main_":
    init_db()
    seed_schedule()
    print("Бот жұмысқа дайын ✅")
    bot.polling(none_stop=True)
