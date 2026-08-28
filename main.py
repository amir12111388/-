# =========================================
# 🌟 FPS Manager PRO v2 🌟
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
# DATABASE
# ===============================

DEFAULT_GROUP = {

    "welcome": True,

    "anti_spam": True,

    "anti_link": True,

    "filter": True,

    "rules": "📜 قوانین گروه تنظیم نشده است",

    "filters": []

}


DEFAULT_DB = {

    "groups": {},

    "users": {},

    "warnings": {},

    "admins": {},

    "messages": {},

    "banned": {},

    "muted": {}

}



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


        # سازگاری نسخه های قدیمی

        for key in DEFAULT_DB:

            if key not in data:

                data[key] = DEFAULT_DB[key]


        return data


    except Exception:

        return DEFAULT_DB.copy()



db = load_db()



# ===============================
# GROUP SYSTEM
# ===============================


def init_group(group_id):

    gid = str(group_id)


    if gid not in db["groups"]:

        db["groups"][gid] = DEFAULT_GROUP.copy()

        db["warnings"][gid] = {}

        db["admins"][gid] = []

        db["banned"][gid] = []

        db["muted"][gid] = {}


        save_db()


    else:

        # اضافه کردن امکانات جدید به گروه های قدیمی

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



# ===============================
# MESSAGE COUNT
# ===============================


def add_message(
        user_id
):

    uid = str(user_id)


    if uid not in db["messages"]:

        db["messages"][uid] = 0


    db["messages"][uid] += 1# =========================================
# 🌟 FPS Manager PRO v2 🌟
# Part 2/4
# =========================================


# ===============================
# ADMIN SYSTEM
# ===============================


def is_admin(
        group_id,
        user_id
):

    gid = str(group_id)
    uid = str(user_id)


    if uid == OWNER_ID:
        return True


    return uid in db["admins"].get(
        gid,
        []
    )



def add_admin(
        group_id,
        user_id
):

    gid = str(group_id)
    uid = str(user_id)


    init_group(group_id)


    if uid not in db["admins"][gid]:

        db["admins"][gid].append(uid)

        save_db()

        return True


    return False




def remove_admin(
        group_id,
        user_id
):

    gid = str(group_id)
    uid = str(user_id)


    if uid in db["admins"].get(gid, []):

        db["admins"][gid].remove(uid)

        save_db()

        return True


    return False




def get_admins(
        group_id
):

    return db["admins"].get(
        str(group_id),
        []
    )



# ===============================
# WARNING SYSTEM
# ===============================


def add_warning(
        group_id,
        user_id
):

    gid = str(group_id)
    uid = str(user_id)


    init_group(group_id)


    if uid not in db["warnings"][gid]:

        db["warnings"][gid][uid] = 0


    db["warnings"][gid][uid] += 1


    save_db()


    return db["warnings"][gid][uid]




def remove_warning(
        group_id,
        user_id
):

    gid = str(group_id)
    uid = str(user_id)


    if uid in db["warnings"].get(gid,{}):

        db["warnings"][gid][uid] = 0

        save_db()

        return True


    return False




def get_warning(
        group_id,
        user_id
):

    return db["warnings"].get(
        str(group_id),
        {}
    ).get(
        str(user_id),
        0
    )



# ===============================
# BAN SYSTEM
# ===============================


def ban_user(
        group_id,
        user_id
):

    gid = str(group_id)
    uid = str(user_id)


    init_group(group_id)


    if uid not in db["banned"][gid]:

        db["banned"][gid].append(uid)

        save_db()

        return True


    return False




def unban_user(
        group_id,
        user_id
):

    gid = str(group_id)
    uid = str(user_id)


    if uid in db["banned"].get(gid,[]):

        db["banned"][gid].remove(uid)

        save_db()

        return True


    return False




def is_banned(
        group_id,
        user_id
):

    return str(user_id) in db["banned"].get(
        str(group_id),
        []
    )



# ===============================
# MUTE SYSTEM
# ===============================


def mute_user(
        group_id,
        user_id,
        minutes
):

    gid = str(group_id)
    uid = str(user_id)


    init_group(group_id)


    db["muted"][gid][uid] = {

        "time": int(time.time()),

        "duration": minutes * 60

    }


    save_db()




def is_muted(
        group_id,
        user_id
):

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



    if time.time() - data["time"] >= data["duration"]:

        del db["muted"][gid][uid]

        save_db()

        return False


    return True




def unmute_user(
        group_id,
        user_id
):

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


spam_data = defaultdict(list)



def check_spam(
        user_id
):

    now = time.time()


    spam_data[user_id] = [

        x for x in spam_data[user_id]

        if now - x < 8

    ]


    spam_data[user_id].append(now)


    return len(spam_data[user_id]) >= 7



# ===============================
# ANTI LINK
# ===============================


def has_link(
        text
):

    links = [

        "http://",

        "https://",

        "www.",

        ".com"

    ]


    for x in links:

        if x in text.lower():

            return True


    return False# =========================================
# 🌟 FPS Manager PRO v2 🌟
# Part 3/4
# =========================================


# ===============================
# HELP TEXT
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
🤖 وضعیت ربات
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

👢 اخراج (با ریپلای)
🚫 بن (با ریپلای)
✅ آنبن (با ریپلای)
🔇 سکوت زمان (با ریپلای)
🔊 حذف سکوت (با ریپلای)


👑 سازنده:
پنل ادمین
"""



# ===============================
# BOT PANEL
# ===============================


def owner_panel():

    return """
👑 پنل سازنده FPS

دستورات:

📊 آمار کل
📢 پیام همگانی
📂 لیست گروه ها
🔄 ریست وضعیت
"""


# ===============================
# GROUP STATS
# ===============================


def group_stats(group_id):

    gid = str(group_id)

    return f"""
📊 آمار گروه

👥 کاربران ثبت شده:
{len(db["users"])}

⚠️ تعداد اخطار:
{len(db["warnings"].get(gid,{}))}

👑 مدیرها:
{len(db["admins"].get(gid,[]))}

🚫 بن شده:
{len(db["banned"].get(gid,[]))}

🤖 وضعیت:
فعال ✅
"""



# ===============================
# COMMAND HANDLER
# ===============================


async def handle_commands(
        event,
        group_id,
        user_id
):

    text = event.raw_text.strip()

    group = get_group(group_id)


    # -------------------------------
    # عمومی
    # -------------------------------


    if text in [
        "راهنما",
        "/help",
        "کمک"
    ]:

        await event.reply(
            help_text()
        )

        return True



    if text == "قوانین":

        await event.reply(
            "📜 قوانین گروه:\n\n"
            + group["rules"]
        )

        return True



    if text == "آمار":

        await event.reply(
            group_stats(group_id)
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
            "🏓 پینگ ربات خوبه ✅"
        )

        return True



    if text == "اخطار من":

        await event.reply(
f"""
⚠️ تعداد اخطار شما:

{get_warning(group_id,user_id)}
"""
        )

        return True



    # -------------------------------
    # پنل سازنده
    # -------------------------------


    if text == "پنل ادمین":

        if str(user_id) == OWNER_ID:

            await event.reply(
                owner_panel()
            )

        else:

            await event.reply(
                "❌ این بخش فقط مخصوص سازنده است"
            )

        return True



    # -------------------------------
    # فقط مدیر
    # -------------------------------


    if not is_admin(
        group_id,
        user_id
    ):

        return False



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




    if text.startswith(
        "افزودن مدیر "
    ):

        uid = text.replace(
            "افزودن مدیر ",
            ""
        )


        if add_admin(
            group_id,
            uid
        ):

            await event.reply(
                "👑 مدیر اضافه شد"
            )

        return True




    if text.startswith(
        "حذف مدیر "
    ):

        uid = text.replace(
            "حذف مدیر ",
            ""
        )


        if remove_admin(
            group_id,
            uid
        ):

            await event.reply(
                "❌ مدیر حذف شد"
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



    return False# =========================================
# 🌟 FPS Manager PRO v2 🌟
# Part 4/4
# =========================================


# ===============================
# WELCOME SYSTEM
# ===============================


async def welcome_user(event):

    try:

        chat = await event.get_chat()

        group_id = chat.id

        group = get_group(group_id)


        if not group["welcome"]:

            return


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

به گروه {getattr(chat,"title","گروه")} خوش آمدید 🌹

برای مشاهده دستورات:

📚 راهنما

🔥 موفق باشید
"""
            )


    except Exception:

        traceback.print_exc()



# ===============================
# MESSAGE HANDLER
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
        # PRIVATE
        # ===========================


        if not getattr(
            chat,
            "megagroup",
            False
        ):


            await event.reply(
f"""
🌟 ربات مدیریت گروه FPS 🌟

سلام {name} عزیز 👋

به ربات مدیریت گروه FPS خوش آمدی 🤖

من برای مدیریت گروه ساخته شدم.

💯 امکانات:

🛡 ضد اسپم
🔗 ضد لینک
👋 خوش آمدگویی
⚠️ سیستم اخطار
👑 مدیریت مدیران

برای استفاده:
ربات را به گروه اضافه کن و در گروه بنویس:

📚 راهنما
"""
            )

            return




        group_id = chat.id


        group = get_group(
            group_id
        )



        # ===========================
        # BAN CHECK
        # ===========================


        if is_banned(
            group_id,
            user_id
        ):

            return



        # ===========================
        # MUTE CHECK
        # ===========================


        if is_muted(
            group_id,
            user_id
        ):

            return



        # ===========================
        # ANTI LINK
        # ===========================


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


                    await event.reply(
f"""
🔗 لینک غیرمجاز حذف شد

⚠️ اخطار:
{warn}
"""
                    )

                    return




        # ===========================
        # ANTI SPAM
        # ===========================


        if group["anti_spam"]:

            if check_spam(
                user_id
            ):

                warn = add_warning(
                    group_id,
                    user_id
                )


                await event.reply(
f"""
🛡 اسپم شناسایی شد

⚠️ اخطار:
{warn}
"""
                )

                return




        # ===========================
        # COMMANDS
        # ===========================


        await handle_commands(
            event,
            group_id,
            user_id
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
