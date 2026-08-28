# =========================================
# 🌟 FPS Manager PRO Ultimate 🌟
# Part 1/5
# =========================================

import os
import json
import time
import random
import asyncio
import traceback

from datetime import datetime
from collections import defaultdict

from splusthon import SoroushClient
from splusthon import events



# ===============================
# CONFIG
# ===============================

SESSION = "splus_manager.session"

DB_FILE = "fps_database.json"

BOT_NAME = "🌟 ربات مدیریت گروه FPS 🌟"

OWNER_ID = "68244916"

BOT_LINK = "https://splus.ir/FPS_BOT"



client = SoroushClient(
    SESSION
)



# ===============================
# TIME SYSTEM
# ===============================


def get_time():

    return datetime.now().strftime(
        "%H:%M:%S"
    )



def get_date():

    return datetime.now().strftime(
        "%Y/%m/%d"
    )



def time_text():

    return f"""
🕒 ساعت:
{get_time()}

📅 تاریخ:
{get_date()}
"""



# ===============================
# DEFAULT SETTINGS
# ===============================


DEFAULT_GROUP = {


    "welcome": True,


    "anti_link": True,


    "anti_spam": True,


    "filter": True,


    "auto_ban": True,


    "rules": "📜 قوانین تنظیم نشده است",


    "filters": [],


    "challenge": []

}




DEFAULT_DB = {


    "groups": {},


    "users": {},


    "messages": {},


    "admins": {},


    "owners": {},


    "warnings": {},


    "banned": {},


    "muted": {},


    "challenge_history": {},


    "global_start": int(time.time())

}




# ===============================
# DATABASE
# ===============================


def save_db():

    try:

        with open(
            DB_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                db,
                f,
                ensure_ascii=False,
                indent=4
            )

    except Exception:

        traceback.print_exc()



def load_db():

    if not os.path.exists(DB_FILE):

        return DEFAULT_DB.copy()


    try:

        with open(
            DB_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)



        for key,value in DEFAULT_DB.items():

            if key not in data:

                data[key] = value



        return data


    except Exception:

        return DEFAULT_DB.copy()



db = load_db()



# ===============================
# GROUP DATABASE
# ===============================


def init_group(group_id):

    gid = str(group_id)


    if gid not in db["groups"]:

        db["groups"][gid] = DEFAULT_GROUP.copy()

        db["admins"][gid] = []

        db["owners"][gid] = None

        db["warnings"][gid] = {}

        db["banned"][gid] = []

        db["muted"][gid] = {}


        save_db()



    else:

        for key,value in DEFAULT_GROUP.items():

            if key not in db["groups"][gid]:

                db["groups"][gid][key] = value


        save_db()




def get_group(group_id):

    init_group(group_id)

    return db["groups"][str(group_id)]



# ===============================
# USER DATABASE
# ===============================


def save_user(
        user_id,
        name
):

    uid = str(user_id)


    if uid not in db["users"]:

        db["users"][uid] = {


            "name": name,


            "join": int(time.time())

        }


        save_db()




def add_message(user_id):

    uid = str(user_id)


    if uid not in db["messages"]:

        db["messages"][uid] = 0


    db["messages"][uid] += 1# =========================================
# 🌟 FPS Manager PRO Ultimate 🌟
# Part 2/5
# =========================================


# ===============================
# OWNER / ADMIN SYSTEM
# ===============================


def set_owner(group_id, user_id):

    gid = str(group_id)

    init_group(group_id)

    if db["owners"][gid] is None:

        db["owners"][gid] = str(user_id)

        save_db()



def get_owner(group_id):

    return db["owners"].get(
        str(group_id),
        None
    )



def is_owner(group_id, user_id):

    return str(user_id) == str(
        get_owner(group_id)
    ) or str(user_id) == OWNER_ID




def is_admin(group_id, user_id):

    gid = str(group_id)

    uid = str(user_id)


    if is_owner(
        group_id,
        user_id
    ):

        return True


    return uid in db["admins"].get(
        gid,
        []
    )



def add_admin(group_id,user_id):

    gid = str(group_id)

    uid = str(user_id)


    init_group(group_id)


    if uid not in db["admins"][gid]:

        db["admins"][gid].append(uid)

        save_db()

        return True


    return False



def remove_admin(group_id,user_id):

    gid = str(group_id)

    uid = str(user_id)


    if uid in db["admins"].get(gid,[]):

        db["admins"][gid].remove(uid)

        save_db()

        return True


    return False



# ===============================
# WARNING SYSTEM
# ===============================


MAX_WARN = 3



def add_warning(group_id,user_id):

    gid = str(group_id)

    uid = str(user_id)


    init_group(group_id)


    if uid not in db["warnings"][gid]:

        db["warnings"][gid][uid] = 0


    db["warnings"][gid][uid] += 1


    save_db()


    return db["warnings"][gid][uid]




def clear_warning(group_id,user_id):

    gid = str(group_id)

    uid = str(user_id)


    if uid in db["warnings"].get(gid,{}):

        db["warnings"][gid][uid] = 0

        save_db()

        return True


    return False




def get_warning(group_id,user_id):

    return db["warnings"].get(
        str(group_id),
        {}
    ).get(
        str(user_id),
        0
    )



# ===============================
# AUTO BAN
# ===============================


def need_auto_ban(group_id,user_id):

    group = get_group(
        group_id
    )


    if not group["auto_ban"]:

        return False



    return get_warning(
        group_id,
        user_id
    ) >= MAX_WARN




# ===============================
# BAN SYSTEM
# ===============================


def ban_user(group_id,user_id):

    gid = str(group_id)

    uid = str(user_id)


    init_group(group_id)


    if uid not in db["banned"][gid]:

        db["banned"][gid].append(uid)

        save_db()

        return True


    return False



def unban_user(group_id,user_id):

    gid = str(group_id)

    uid = str(user_id)


    if uid in db["banned"].get(gid,[]):

        db["banned"][gid].remove(uid)

        save_db()

        return True


    return False



def is_banned(group_id,user_id):

    return str(user_id) in db["banned"].get(
        str(group_id),
        []
    )



# ===============================
# MUTE SYSTEM
# ===============================


def mute_user(group_id,user_id,minutes):

    gid = str(group_id)

    uid = str(user_id)


    db["muted"][gid][uid] = {

        "start": int(time.time()),

        "duration": minutes * 60

    }


    save_db()




def is_muted(group_id,user_id):

    gid = str(group_id)

    uid = str(user_id)


    data = db["muted"].get(
        gid,
        {}
    ).get(uid)



    if not data:

        return False



    if time.time() - data["start"] >= data["duration"]:

        del db["muted"][gid][uid]

        save_db()

        return False



    return True




def unmute_user(group_id,user_id):

    gid = str(group_id)

    uid = str(user_id)


    if uid in db["muted"].get(gid,{}):

        del db["muted"][gid][uid]

        save_db()

        return True


    return False



# ===============================
# ANTI SPAM
# ===============================


spam_cache = defaultdict(list)



def check_spam(user_id):

    now = time.time()


    spam_cache[user_id] = [

        x for x in spam_cache[user_id]

        if now - x < 8

    ]


    spam_cache[user_id].append(now)


    return len(spam_cache[user_id]) >= 7



# ===============================
# ANTI LINK
# ===============================


def has_link(text):

    bad = [

        "http://",

        "https://",

        "www.",

        ".com",

        ".ir"

    ]


    text = text.lower()


    for item in bad:

        if item in text:

            return True


    return False



# ===============================
# FILTER WORD
# ===============================


def add_filter(group_id,word):

    gid = str(group_id)

    init_group(group_id)


    if word not in db["groups"][gid]["filters"]:

        db["groups"][gid]["filters"].append(word)

        save_db()



def remove_filter(group_id,word):

    gid = str(group_id)


    if word in db["groups"][gid]["filters"]:

        db["groups"][gid]["filters"].remove(word)

        save_db()



def has_filter(group_id,text):

    filters = db["groups"].get(
        str(group_id),
        {}
    ).get(
        "filters",
        []
    )


    for word in filters:

        if word in text:

            return True


    return False# =========================================
# 🌟 FPS Manager PRO Ultimate 🌟
# Part 3/5
# =========================================


# ===============================
# CHALLENGE SYSTEM
# ===============================


CHALLENGES = [

"از چه چیزی بیشتر خوشت میاد؟",

"از چه چیزی بدت میاد؟",

"اگر یک قدرت داشتی چی انتخاب می‌کردی؟",

"بزرگ‌ترین هدف زندگی‌ات چیه؟",

"اگر پول نامحدود داشتی چه کاری انجام می‌دادی؟",

"بهترین خاطره‌ات چیه؟",

"دوست داری به کجا سفر کنی؟",

"اگر یک روز جای یک آدم معروف بودی چه می‌کردی؟",

"یک استعداد مخفی داری؟",

"آخرین چیزی که خوشحالت کرد چی بود؟",

"اگر مدیر گروه بودی چه قانونی می‌گذاشتی؟",

"بهترین بازی که انجام دادی چی بوده؟",

"از چه کاری پشیمونی؟",

"دوست داری چه چیزی یاد بگیری؟",

"اگر زمان برمی‌گشت عقب چه چیزی را تغییر می‌دادی؟",

# ادامه سوال‌ها در نسخه کامل تا 100 عدد قرار می‌گیرد

]



def get_challenge(user_id):

    uid = str(user_id)


    if uid not in db["challenge_history"]:

        db["challenge_history"][uid] = []



    used = db["challenge_history"][uid]


    available = [

        x for x in range(
            len(CHALLENGES)
        )

        if x not in used

    ]



    if not available:

        db["challenge_history"][uid] = []

        available = list(
            range(
                len(CHALLENGES)
            )
        )



    number = random.choice(
        available
    )


    db["challenge_history"][uid].append(
        number
    )


    save_db()


    return number + 1, CHALLENGES[number]



# ===============================
# SMART ANSWER
# ===============================


SMART = {


"سلام":[

"سلام عزیز 👋🌟",

"ارادت 🔥 خوش آمدی"

],


"چطوری":[

"عالی‌ام 🤖 آماده مدیریت گروه هستم",

"خوبم عزیز، ممنون 🌹"

],


"خوبی":[

"خوبم 😎",

"عالی هستم 🔥"

],


"ربات":[

"جانم؟ 🤖",

"FPS در خدمت است 👑"

],


"صبح بخیر":[

"صبح شما هم بخیر ☀️"

],


"شب بخیر":[

"شب شما هم بخیر 🌙"

]

}



def smart_answer(text):

    text = text.lower()


    for key,value in SMART.items():

        if key in text:

            return random.choice(
                value
            )


    return None



# ===============================
# USER PROFILE
# ===============================


def profile(user_id):

    uid = str(user_id)


    data = db["users"].get(
        uid,
        {}
    )


    name = data.get(
        "name",
        "کاربر"
    )


    messages = db["messages"].get(
        uid,
        0
    )


    join = data.get(
        "join",
        time.time()
    )


    return f"""
👤 پروفایل

🏷 نام:
{name}

💬 پیام‌ها:
{messages}

📅 ورود:
{datetime.fromtimestamp(join).strftime("%Y/%m/%d")}

⚠️ اخطار:
0
"""



# ===============================
# WELCOME TEXT
# ===============================


def welcome_text(name,group):

    return f"""
🌟 ربات مدیریت گروه FPS 🌟

سلام {name} عزیز 👋

به گروه {group} خوش آمدید 🌹

برای دیدن دستورات:

📚 راهنما
"""



# ===============================
# LEFT TEXT
# ===============================


def left_text(name):

    return f"""
👋 {name} گروه را ترک کرد.

🕒 ساعت:
{get_time()}

📅 تاریخ:
{get_date()}
"""# =========================================
# 🌟 FPS Manager PRO Ultimate 🌟
# Part 4/5
# =========================================


# ===============================
# HELP
# ===============================


def help_text():

    return """
🌟 ربات مدیریت گروه FPS 🌟


📚 دستورات عمومی:

📖 راهنما
📜 قوانین
🟢 فعال
📊 آمار
🆔 آیدی
👤 پروفایل
🎯 چالش
🏓 پینگ


👮 دستورات مدیر:


📜 تنظیم قوانین متن


👑 افزودن مدیر
❌ حذف مدیر
📋 لیست مدیرها


⚠️ اخطار
🧹 حذف اخطار


🚫 بن
✅ آنبن
👢 اخراج


🔇 سکوت
🔊 حذف سکوت


🔗 فعال ضد لینک
🔗 خاموش ضد لینک


🛡 فعال ضد اسپم
🛡 خاموش ضد اسپم


🚫 افزودن فیلتر
✅ حذف فیلتر


⚠️ فعال بن خودکار
⚠️ خاموش بن خودکار


👑 سازنده:

پنل ادمین
"""



# ===============================
# STATS
# ===============================


def stats():

    return f"""
📊 آمار FPS


👥 کاربران:
{len(db["users"])}


📂 گروه‌ها:
{len(db["groups"])}


⚠️ اخطارها:
{len(db["warnings"])}


🕒 شروع ربات:

{datetime.fromtimestamp(
db["global_start"]
).strftime("%Y/%m/%d %H:%M")}
"""



# ===============================
# ACTIVE
# ===============================


def active(group_id):

    owner = get_owner(
        group_id
    )


    name = "نامشخص"


    if owner:

        if str(owner) in db["users"]:

            name = db["users"][str(owner)]["name"]



    return f"""
✅ ربات فعال است!


👑 مالک گروه:
{name}


🆔 آیدی مالک:
{owner}


🔹 فقط مالک گروه می‌تواند ربات را مدیریت کند.


🔹 برای مشاهده دستورات:

راهنما


📌 https://splus.ir/FPS_BOT
"""



# ===============================
# OWNER PANEL
# ===============================


def owner_panel():

    return """
👑 پنل سازنده FPS


📊 آمار کل

👥 تعداد کاربران

📂 تعداد گروه‌ها

🤖 وضعیت ربات

📢 پیام همگانی

🗑 پاکسازی دیتابیس


دستورات فقط برای:

68244916
"""



# ===============================
# COMMAND PROCESSOR
# ===============================


async def commands(event,group_id,user_id):


    text = event.raw_text.strip()



    # عمومی


    if text in [
        "راهنما",
        "کمک"
    ]:

        await event.reply(
            help_text()
        )

        return True




    if text == "فعال":

        await event.reply(
            active(group_id)
        )

        return True




    if text == "آمار":

        await event.reply(
            stats()
        )

        return True




    if text == "پروفایل":

        await event.reply(
            profile(user_id)
        )

        return True




    if text == "چالش":

        number,question = get_challenge(
            user_id
        )


        await event.reply(
f"""
🎯 چالش FPS


🔢 شماره:
{number}


❓ سوال:

{question}
"""
        )

        return True




    if text == "پینگ":

        await event.reply(
            "🏓 FPS آنلاین است ✅"
        )

        return True




    if text == "آیدی":

        await event.reply(
f"🆔 آیدی:\n{user_id}"
        )

        return True




    # پنل سازنده


    if text == "پنل ادمین":

        if str(user_id) == OWNER_ID:

            await event.reply(
                owner_panel()
            )

        else:

            await event.reply(
                "❌ دسترسی ندارید"
            )


        return True



    # فقط مدیر


    if not is_admin(
        group_id,
        user_id
    ):

        return False



    group = get_group(
        group_id
    )



    if text.startswith(
        "تنظیم قوانین "
    ):

        group["rules"] = text.replace(
            "تنظیم قوانین ",
            ""
        )

        save_db()

        await event.reply(
            "✅ قوانین تغییر کرد"
        )

        return True




    if text == "فعال ضد لینک":

        group["anti_link"] = True

        save_db()

        await event.reply(
            "🔗 ضد لینک فعال شد"
        )

        return True




    if text == "خاموش ضد لینک":

        group["anti_link"] = False

        save_db()

        await event.reply(
            "🔗 ضد لینک خاموش شد"
        )

        return True




    if text == "فعال ضد اسپم":

        group["anti_spam"] = True

        save_db()

        await event.reply(
            "🛡 ضد اسپم فعال شد"
        )

        return True




    if text == "خاموش ضد اسپم":

        group["anti_spam"] = False

        save_db()

        await event.reply(
            "🛡 ضد اسپم خاموش شد"
        )

        return True




    if text == "فعال بن خودکار":

        group["auto_ban"] = True

        save_db()

        await event.reply(
            "⚠️ بن خودکار فعال شد"
        )

        return True




    if text == "خاموش بن خودکار":

        group["auto_ban"] = False

        save_db()

        await event.reply(
            "⚠️ بن خودکار خاموش شد"
        )

        return True



    return False# =========================================
# 🌟 FPS Manager PRO Ultimate 🌟
# Part 5/5
# =========================================


# ===============================
# GROUP JOIN / LEFT
# ===============================


@client.on(events.ChatAction)
async def chat_action(event):

    try:

        chat = await event.get_chat()

        group_id = chat.id

        init_group(group_id)



        # ورود کاربر

        if event.user_joined or event.user_added:

            user = await event.get_user()

            name = getattr(
                user,
                "first_name",
                "کاربر"
            )


            save_user(
                user.id,
                name
            )


            await event.reply(
                welcome_text(
                    name,
                    getattr(chat,"title","گروه")
                )
            )



        # خروج کاربر

        if event.user_left or event.user_kicked:


            user = await event.get_user()


            name = getattr(
                user,
                "first_name",
                "کاربر"
            )


            await event.reply(
                left_text(name)
            )


    except Exception:

        traceback.print_exc()



# ===============================
# MESSAGE HANDLER
# ===============================


@client.on(events.NewMessage)
async def new_message(event):

    try:


        text = event.raw_text.strip()


        sender = await event.get_sender()


        if not sender:

            return



        user_id = sender.id


        name = getattr(
            sender,
            "first_name",
            "کاربر"
        )


        save_user(
            user_id,
            name
        )


        add_message(
            user_id
        )



        chat = await event.get_chat()



        # ===========================
        # PRIVATE
        # ===========================


        if not getattr(
            chat,
            "megagroup",
            False
        ):


            if text == "پنل ادمین":


                if str(user_id) == OWNER_ID:

                    await event.reply(
                        owner_panel()
                    )

                else:

                    await event.reply(
                        "❌ این بخش فقط مخصوص سازنده است"
                    )


            else:

                await event.reply(
f"""
🌟 ربات مدیریت گروه FPS 🌟

سلام {name} عزیز 👋

به ربات مدیریت گروه FPS خوش آمدی 🤖


من برای مدیریت گروه ساخته شدم:


🛡 ضد اسپم
🔗 ضد لینک
⚠️ اخطار
👋 خوش آمد
🎯 چالش


ربات را به گروه اضافه کن و بنویس:

📚 راهنما
"""
                )


            return




        # ===========================
        # GROUP
        # ===========================


        group_id = chat.id


        group = get_group(
            group_id
        )



        # ثبت مالک اولین نفر

        if not get_owner(group_id):

            set_owner(
                group_id,
                user_id
            )



        # کاربران ممنوع

        if is_banned(
            group_id,
            user_id
        ):

            return



        # سکوت

        if is_muted(
            group_id,
            user_id
        ):

            return




        # ضد لینک


        if group["anti_link"]:


            if has_link(text):


                if not is_admin(
                    group_id,
                    user_id
                ):


                    warn = add_warning(
                        group_id,
                        user_id
                    )


                    if need_auto_ban(
                        group_id,
                        user_id
                    ):


                        ban_user(
                            group_id,
                            user_id
                        )


                        await event.reply(
f"""
🚫 کاربر به دلیل ۳ اخطار بن شد.

⚠️ اخطار:
{warn}/3
"""
                        )


                    else:


                        await event.reply(
f"""
🔗 لینک غیرمجاز

⚠️ اخطار:
{warn}/3
"""
                        )


                    return




        # ضد اسپم


        if group["anti_spam"]:


            if check_spam(user_id):


                warn = add_warning(
                    group_id,
                    user_id
                )


                await event.reply(
f"""
🛡 اسپم شناسایی شد

⚠️ اخطار:
{warn}/3
"""
                )


                return



        # فیلتر


        if group["filter"]:


            if has_filter(
                group_id,
                text
            ):


                warn = add_warning(
                    group_id,
                    user_id
                )


                await event.reply(
f"""
🚫 کلمه غیرمجاز

⚠️ اخطار:
{warn}/3
"""
                )


                return




        # دستورات


        done = await commands(
            event,
            group_id,
            user_id
        )


        if done:

            return



        # جواب هوشمند


        answer = smart_answer(
            text
        )


        if answer:

            await event.reply(
                answer
            )



    except Exception:

        traceback.print_exc()




# ===============================
# START
# ===============================


def start_bot():


    print(
        "🌟 ربات مدیریت گروه FPS 🌟"
    )


    try:


        client.start()


        print(
            "✅ ربات روشن شد"
        )


        client.run_until_disconnected()



    except Exception as e:


        print(
            "ERROR:",
            e
        )


        traceback.print_exc()




if __name__ == "__main__":

    start_bot()
