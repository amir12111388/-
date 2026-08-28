# =========================================
# 🌟 FPS Manager PRO v3 🌟
# Part 1/4
# =========================================

import os
import json
import time
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


# ===============================
# CLIENT
# ===============================

client = SoroushClient(
    SESSION
)



# ===============================
# DEFAULT SETTINGS
# ===============================

DEFAULT_GROUP = {

    "welcome": True,

    "anti_spam": True,

    "anti_link": True,

    "filter": True,

    "auto_ban": True,

    "rules": "📜 قوانین تنظیم نشده است",

    "filters": []

}



DEFAULT_DB = {

    "groups": {},

    "users": {},

    "admins": {},

    "warnings": {},

    "banned": {},

    "muted": {},

    "messages": {},

    "start_time": int(time.time())

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


    except:

        return DEFAULT_DB.copy()



db = load_db()



# ===============================
# GROUP INIT
# ===============================


def init_group(group_id):

    gid = str(group_id)


    if gid not in db["groups"]:

        db["groups"][gid] = DEFAULT_GROUP.copy()

        db["admins"][gid] = []

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
# USER SYSTEM
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



def add_message(
        user_id
):

    uid = str(user_id)


    if uid not in db["messages"]:

        db["messages"][uid] = 0


    db["messages"][uid] += 1# =========================================
# 🌟 FPS Manager PRO v3 🌟
# Part 2/4
# =========================================


# ===============================
# ADMIN SYSTEM
# ===============================


def is_admin(group_id, user_id):

    gid = str(group_id)
    uid = str(user_id)


    if uid == OWNER_ID:

        return True


    return uid in db["admins"].get(
        gid,
        []
    )



def add_admin(group_id, user_id):

    gid = str(group_id)
    uid = str(user_id)


    init_group(group_id)


    if uid not in db["admins"][gid]:

        db["admins"][gid].append(uid)

        save_db()

        return True


    return False



def remove_admin(group_id, user_id):

    gid = str(group_id)
    uid = str(user_id)


    if uid in db["admins"].get(gid, []):

        db["admins"][gid].remove(uid)

        save_db()

        return True


    return False



# ===============================
# WARNING SYSTEM
# ===============================


MAX_WARNING = 3



def add_warning(group_id, user_id):

    gid = str(group_id)
    uid = str(user_id)


    init_group(group_id)


    if uid not in db["warnings"][gid]:

        db["warnings"][gid][uid] = 0


    db["warnings"][gid][uid] += 1


    save_db()


    return db["warnings"][gid][uid]



def clear_warning(group_id, user_id):

    gid = str(group_id)
    uid = str(user_id)


    if uid in db["warnings"].get(gid,{}):

        db["warnings"][gid][uid] = 0

        save_db()

        return True


    return False



def get_warning(group_id, user_id):

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


def auto_ban_check(group_id, user_id):

    warn = get_warning(
        group_id,
        user_id
    )


    group = get_group(
        group_id
    )


    if (
        warn >= MAX_WARNING
        and group["auto_ban"]
    ):

        ban_user(
            group_id,
            user_id
        )

        return True


    return False



# ===============================
# BAN SYSTEM
# ===============================


def ban_user(group_id, user_id):

    gid = str(group_id)
    uid = str(user_id)


    init_group(group_id)


    if uid not in db["banned"][gid]:

        db["banned"][gid].append(uid)

        save_db()

        return True


    return False



def unban_user(group_id, user_id):

    gid = str(group_id)
    uid = str(user_id)


    if uid in db["banned"].get(gid, []):

        db["banned"][gid].remove(uid)

        save_db()

        return True


    return False



def is_banned(group_id, user_id):

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

        "time": minutes * 60

    }


    save_db()



def is_muted(group_id,user_id):

    gid = str(group_id)
    uid = str(user_id)


    data = db["muted"].get(
        gid,
        {}
    ).get(
        uid
    )


    if not data:

        return False


    if time.time() - data["start"] >= data["time"]:

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
# SECURITY
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



def has_link(text):

    words = [

        "http://",

        "https://",

        "www.",

        ".com"

    ]


    text = text.lower()


    for word in words:

        if word in text:

            return True


    return False# =========================================
# 🌟 FPS Manager PRO v3 🌟
# Part 3/4
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
📊 آمار
🆔 آیدی
🏓 پینگ
⚠️ اخطار من


👮 دستورات مدیر:

📜 تنظیم قوانین متن

👑 افزودن مدیر
❌ حذف مدیر
📋 لیست مدیرها

⚠️ حذف اخطار

🚫 افزودن فیلتر
✅ حذف فیلتر

🔗 فعال ضد لینک
🔗 خاموش ضد لینک

🛡 فعال ضد اسپم
🛡 خاموش ضد اسپم

👋 فعال خوش آمد
👋 خاموش خوش آمد

⚠️ فعال بن خودکار
⚠️ خاموش بن خودکار

👢 اخراج (با ریپلای)
🚫 بن (با ریپلای)
✅ آنبن
🔇 سکوت
🔊 حذف سکوت


👑 سازنده:

پنل ادمین
"""



# ===============================
# OWNER PANEL
# ===============================


def owner_panel():

    return """
👑 پنل سازنده FPS

دستورات:

📊 آمار کل
👥 تعداد کاربران
📂 تعداد گروه ها
🤖 وضعیت ربات
📢 پیام همگانی

🗑 پاک کردن دیتابیس
"""



# ===============================
# GLOBAL STATS
# ===============================


def global_stats():

    return f"""
📊 آمار کل FPS

👥 کاربران:
{len(db["users"])}

📂 گروه ها:
{len(db["groups"])}

⚠️ اخطارها:
{len(db["warnings"])}

🕒 شروع:
{datetime.fromtimestamp(db["start_time"])}
"""



# ===============================
# COMMAND HANDLER
# ===============================


async def handle_commands(event,group_id,user_id):


    text = event.raw_text.strip()


    group = get_group(
        group_id
    )


    # عمومی

    if text in [
        "راهنما",
        "کمک",
        "/help"
    ]:

        await event.reply(
            help_text()
        )

        return True



    if text == "قوانین":

        await event.reply(
            "📜 قوانین:\n\n"
            + group["rules"]
        )

        return True



    if text == "آیدی":

        await event.reply(
f"""
🆔 آیدی شما:

{user_id}
"""
        )

        return True



    if text == "پینگ":

        await event.reply(
            "🏓 پینگ FPS عالیه ✅"
        )

        return True



    if text == "آمار":

        await event.reply(
            global_stats()
        )

        return True



    if text == "اخطار من":

        await event.reply(
f"""
⚠️ اخطار شما:

{get_warning(group_id,user_id)}/3
"""
        )

        return True



    # ===========================
    # OWNER PANEL
    # ===========================


    if text == "پنل ادمین":

        if str(user_id) == OWNER_ID:

            await event.reply(
                owner_panel()
            )

        else:

            await event.reply(
                "❌ این پنل فقط برای سازنده است"
            )

        return True



    if str(user_id) == OWNER_ID:


        if text == "آمار کل":

            await event.reply(
                global_stats()
            )

            return True



        if text == "تعداد کاربران":

            await event.reply(
f"👥 تعداد کاربران: {len(db['users'])}"
            )

            return True



        if text == "تعداد گروه ها":

            await event.reply(
f"📂 تعداد گروه ها: {len(db['groups'])}"
            )

            return True



        if text == "وضعیت ربات":

            await event.reply(
                "🤖 FPS Manager فعال است ✅"
            )

            return True



    # فقط مدیر

    if not is_admin(
        group_id,
        user_id
    ):

        return False



    if text.startswith("تنظیم قوانین "):

        group["rules"] = text.replace(
            "تنظیم قوانین ",
            ""
        )

        save_db()

        await event.reply(
            "✅ قوانین تغییر کرد"
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



    return False# =========================================
# 🌟 FPS Manager PRO v3 🌟
# Part 4/4
# =========================================


# ===============================
# WELCOME
# ===============================


async def send_welcome(event):

    try:

        chat = await event.get_chat()

        title = getattr(
            chat,
            "title",
            "گروه"
        )


        users = getattr(
            event,
            "users",
            []
        )


        for user in users:

            name = getattr(
                user,
                "first_name",
                "کاربر"
            )


            await event.reply(
f"""
🌟 ربات مدیریت گروه FPS 🌟

سلام {name} عزیز 👋

به گروه {title} خوش آمدید 🌹

برای مشاهده امکانات ربات:

📚 راهنما

🔥 موفق باشید
"""
            )


    except Exception:

        traceback.print_exc()



# ===============================
# MESSAGE EVENT
# ===============================


@client.on(events.NewMessage)
async def message_handler(event):

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
        # PV BOT
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
                        "❌ دسترسی ندارید"
                    )

                return



            await event.reply(
f"""
🌟 ربات مدیریت گروه FPS 🌟

سلام {name} عزیز 👋

به ربات مدیریت گروه FPS خوش آمدی 🤖

من برای مدیریت گروه ساخته شدم.

امکانات:

🛡 ضد اسپم
🔗 ضد لینک
👋 خوش آمدگویی
⚠️ سیستم اخطار
👑 مدیریت مدیران

ربات را به گروه خود اضافه کن و بنویس:

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



        # بن شده

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


                    if auto_ban_check(
                        group_id,
                        user_id
                    ):


                        await event.reply(
f"""
🚫 کاربر به دلیل رسیدن به ۳ اخطار بن شد.

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

            if check_spam(
                user_id
            ):


                warn = add_warning(
                    group_id,
                    user_id
                )


                if auto_ban_check(
                    group_id,
                    user_id
                ):

                    await event.reply(
                        "🚫 کاربر با ۳ اخطار بن شد"
                    )

                else:

                    await event.reply(
f"🛡 اسپم شناسایی شد\n⚠️ {warn}/3"
                    )

                return



        await handle_commands(
            event,
            group_id,
            user_id
        )



    except Exception:

        traceback.print_exc()



# ===============================
# START BOT
# ===============================


def start_bot():

    print(
        "🌟 ربات مدیریت گروه FPS 🌟"
    )


    try:

        loop = asyncio.new_event_loop()

        asyncio.set_event_loop(
            loop
        )


        client.start()


        print(
            "✅ LOGIN OK"
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
