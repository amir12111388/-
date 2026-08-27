# =========================================
# 🌟 FPS Group Manager v5.1 🌟
# main.py
# Part 1/4
# =========================================

import os
import json
import time
import traceback
from collections import defaultdict
from datetime import datetime

from splusthon import SoroushClient
from splusthon import events


# ===============================
# CONFIG
# ===============================

BOT_NAME = "🌟 ربات مدیریت گروه FPS 🌟"

OWNER_ID = 68244916

SESSION = "splus_manager.session"

DB_FILE = "fps_database.json"

VERSION = "5.1"


# ===============================
# CLIENT
# ===============================

client = SoroushClient(
    SESSION
)


# ===============================
# DATABASE
# ===============================

DEFAULT_DB = {

    "users": {},

    "groups": {},

    "warnings": {},

    "admins": {},

    "filters": {},

    "stats": {
        "messages": 0,
        "groups": 0
    }

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

        return DEFAULT_DB


    try:

        with open(
            DB_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)


        for key in DEFAULT_DB:

            if key not in data:

                data[key] = DEFAULT_DB[key]


        return data


    except Exception:

        return DEFAULT_DB



db = load_db()



# ===============================
# TIME
# ===============================

def get_time():

    return datetime.now().strftime(
        "%H:%M"
    )



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

            "join": int(time.time()),

            "messages": 0

        }


    db["users"][uid]["messages"] += 1


    save_db()



def get_name(
        user_id
):

    return db["users"].get(
        str(user_id),
        {}
    ).get(
        "name",
        "کاربر"
    )



# ===============================
# GROUP SYSTEM
# ===============================


def create_group(
        group_id
):

    gid = str(group_id)


    if gid not in db["groups"]:

        db["groups"][gid] = {

            "welcome": True,

            "anti_link": True,

            "anti_spam": True,

            "filter": True,

            "rules": "📜 قوانینی تنظیم نشده است"

        }


        db["warnings"][gid] = {}

        db["admins"][gid] = []

        db["filters"][gid] = []


        db["stats"]["groups"] += 1


        save_db()



def get_group(
        group_id
):

    create_group(
        group_id
    )

    return db["groups"][str(group_id)]



# ===============================
# OWNER
# ===============================


def is_owner(
        user_id
):

    return int(user_id) == OWNER_ID



def is_admin(
        group_id,
        user_id
):

    if is_owner(user_id):

        return True


    return str(user_id) in db["admins"].get(
        str(group_id),
        []
    )# =========================================
# 🌟 FPS Group Manager v5.1 🌟
# Part 2/4
# =========================================


# ===============================
# WARNING SYSTEM
# ===============================


def add_warning(
        group_id,
        user_id
):

    gid = str(group_id)

    uid = str(user_id)


    if uid not in db["warnings"].get(gid, {}):

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


    if uid in db["warnings"].get(gid, {}):

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
# ADMIN MANAGEMENT
# ===============================


def add_admin(
        group_id,
        user_id
):

    gid = str(group_id)

    uid = str(user_id)


    if uid not in db["admins"].get(gid, []):

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
# FILTER SYSTEM
# ===============================


def add_filter(
        group_id,
        word
):

    gid = str(group_id)


    if word not in db["filters"].get(gid, []):

        db["filters"][gid].append(word)

        save_db()

        return True


    return False





def delete_filter(
        group_id,
        word
):

    gid = str(group_id)


    if word in db["filters"].get(gid, []):

        db["filters"][gid].remove(word)

        save_db()

        return True


    return False





def check_filter(
        group_id,
        text
):

    for word in db["filters"].get(
        str(group_id),
        []
    ):

        if word in text:

            return True


    return False





# ===============================
# ANTI SPAM
# ===============================


spam_users = defaultdict(list)



def check_spam(
        user_id
):

    now = time.time()


    spam_users[user_id] = [

        t for t in spam_users[user_id]

        if now - t < 10

    ]


    spam_users[user_id].append(
        now
    )


    if len(spam_users[user_id]) >= 7:

        return True


    return False





# ===============================
# ANTI LINK
# ===============================


def check_link(
        text
):

    words = [

        "http://",

        "https://",

        "www.",

        ".com",

        ".ir",

        "t.me"

    ]


    text = text.lower()


    for word in words:

        if word in text:

            return True


    return False





# ===============================
# GROUP STATS
# ===============================


def get_stats(
        group_id
):

    return f"""

📊 آمار FPS Manager


👥 کاربران:
{len(db["users"])}


💬 پیام‌ها:
{db["stats"]["messages"]}


⚠️ اخطارهای گروه:
{len(db["warnings"].get(str(group_id), {}))}


🚫 فیلترها:
{len(db["filters"].get(str(group_id), []))}


🕒 ساعت:
{get_time()}

"""# =========================================
# 🌟 FPS Group Manager v5.1 🌟
# Part 3/4
# =========================================


# ===============================
# HELP TEXT
# ===============================


HELP_TEXT = """

🌟 ربات مدیریت گروه FPS 🌟


📚 دستورات عمومی:


📖 راهنما

📜 قوانین

📊 آمار

🆔 آیدی

🏓 پینگ

🤖 ربات

⚠️ اخطار من

👑 مدیرها

🚫 فیلترها


━━━━━━━━━━━━━━


👮 دستورات مدیر:


📜 تنظیم قوانین متن

👑 افزودن مدیر

❌ حذف مدیر

📋 لیست مدیرها

⚠️ حذف اخطار


🚫 افزودن فیلتر

✅ حذف فیلتر


🔗 فعال ضد لینک

🔕 خاموش ضد لینک


🛡 فعال ضد اسپم

🔕 خاموش ضد اسپم


👋 فعال خوش آمد

👋 خاموش خوش آمد


━━━━━━━━━━━━━━


🔥 FPS Manager v5.1

"""





OWNER_PANEL = """

👑 پنل سازنده FPS 👑


📊 آمار ربات

👥 تعداد کاربران

🏠 تعداد گروه‌ها

💬 تعداد پیام‌ها


⚙️ تنظیمات اصلی

🔄 مدیریت دیتابیس


🔥 مخصوص سازنده

"""






# ===============================
# COMMANDS
# ===============================


async def commands_handler(
        event,
        group_id,
        user_id
):


    text = event.raw_text.strip()


    group = get_group(
        group_id
    )



    # عمومی


    if text in [
        "راهنما",
        "/help",
        "کمک"
    ]:


        await event.reply(
            HELP_TEXT
        )


        return True





    if text == "قوانین":


        await event.reply(

            "📜 قوانین گروه:\n\n"
            +
            group["rules"]

        )


        return True






    if text == "آمار":


        await event.reply(

            get_stats(
                group_id
            )

        )


        return True






    if text == "آیدی":


        await event.reply(

f"""

🆔 اطلاعات شما:


👤 نام:
{get_name(user_id)}


🔢 آیدی:
{user_id}

"""

        )


        return True






    if text == "پینگ":


        await event.reply(

f"""

🏓 Pong!


⚡ FPS Manager

🕒 {get_time()}

"""

        )


        return True






    if text == "ربات":


        await event.reply(

f"""

🤖 {BOT_NAME}


🚀 نسخه:
{VERSION}


🕒 ساعت:
{get_time()}

"""

        )


        return True






    if text == "اخطار من":


        await event.reply(

f"""

⚠️ اخطار شما:


{get_warning(
    group_id,
    user_id
)}

"""

        )


        return True





    if text == "مدیرها":


        admins = get_admins(
            group_id
        )


        await event.reply(

"👑 مدیرهای گروه:\n\n"
+
"\n".join(admins)

        )


        return True






    if text == "فیلترها":


        filters = db["filters"].get(
            str(group_id),
            []
        )


        await event.reply(

"🚫 فیلترهای گروه:\n\n"
+
"\n".join(filters)

        )


        return True







    # فقط مدیر


    if not is_admin(
        group_id,
        user_id
    ):

        return False







    # قوانین


    if text.startswith(
        "تنظیم قوانین "
    ):


        group["rules"] = text.replace(
            "تنظیم قوانین ",
            ""
        )


        save_db()


        await event.reply(
            "📜 قوانین تغییر کرد ✅"
        )


        return True






    # مدیر


    if text.startswith(
        "افزودن مدیر "
    ):


        uid = text.replace(
            "افزودن مدیر ",
            ""
        )


        add_admin(
            group_id,
            uid
        )


        await event.reply(
            "👑 مدیر اضافه شد ✅"
        )


        return True






    if text.startswith(
        "حذف مدیر "
    ):


        uid = text.replace(
            "حذف مدیر ",
            ""
        )


        remove_admin(
            group_id,
            uid
        )


        await event.reply(
            "❌ مدیر حذف شد"
        )


        return True






    if text == "فعال ضد لینک":


        group["anti_link"] = True

        save_db()


        await event.reply(
            "🔗 ضد لینک فعال شد ✅"
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





    if text == "فعال خوش آمد":


        group["welcome"] = True

        save_db()


        await event.reply(
            "👋 خوش آمد فعال شد"
        )


        return True





    if text == "خاموش خوش آمد":


        group["welcome"] = False

        save_db()


        await event.reply(
            "👋 خوش آمد خاموش شد"
        )


        return True





    return False# =========================================
# 🌟 FPS Group Manager v5.1 🌟
# Part 4/4
# =========================================



# ===============================
# OWNER PRIVATE PANEL
# ===============================


async def owner_panel(
        event,
        user_id
):

    if int(user_id) != OWNER_ID:

        return False


    text = event.raw_text.strip()


    if text == "پنل ادمین":


        await event.reply(

f"""
👑 پنل سازنده FPS 👑


📊 آمار ربات


👥 کاربران:
{len(db["users"])}


🏠 گروه‌ها:
{len(db["groups"])}


💬 پیام‌ها:
{db["stats"]["messages"]}


🕒 ساعت:
{get_time()}


🔥 FPS Manager

"""

        )


        return True


    return False






# ===============================
# PRIVATE / GROUP MESSAGE
# ===============================


@client.on(events.NewMessage)
async def message_handler(event):

    try:


        text = event.raw_text.strip()


        sender = await event.get_sender()


        if sender is None:

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



        chat = await event.get_chat()



        # ==========================
        # PRIVATE
        # ==========================


        if not getattr(
            chat,
            "megagroup",
            False
        ):


            if await owner_panel(
                event,
                user_id
            ):

                return



            await event.reply(

f"""
سلام {name} عزیز 👋


به ربات مدیریت گروه FPS خوش اومدی! 👾


من رو به گپت اضافه کن تا گپ رو مدیریت کنم 💯


🎈 استفاده از من کاملاً رایگانه


🔷 لینک گروه رو بفرست
یا
➕ من رو به گروه اضافه کن


🌟 FPS Manager 🌟

"""

            )


            return






        # ==========================
        # GROUP
        # ==========================


        group_id = chat.id


        group = get_group(
            group_id
        )



        # پیام شمارنده


        db["stats"]["messages"] += 1

        save_db()





        # ضد لینک


        if group["anti_link"]:


            if check_link(text):


                warn = add_warning(
                    group_id,
                    user_id
                )


                await event.reply(

f"""
🔗 ارسال لینک ممنوع است!


⚠️ اخطار:
{warn}

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


                await event.reply(

f"""
🛡 اسپم شناسایی شد!


⚠️ اخطار:
{warn}

"""

                )


                return






        # فیلتر


        if group["filter"]:


            if check_filter(
                group_id,
                text
            ):


                warn = add_warning(
                    group_id,
                    user_id
                )


                await event.reply(

f"""
🚫 کلمه ممنوعه!


⚠️ اخطار:
{warn}

"""

                )


                return






        await commands_handler(
            event,
            group_id,
            user_id
        )



    except Exception:


        traceback.print_exc()







# ===============================
# WELCOME NEW MEMBERS
# ===============================


@client.on(events.ChatAction)
async def welcome_handler(event):

    try:


        if not event.user_joined:

            return



        user = await event.get_user()


        group = get_group(
            event.chat_id
        )


        if not group["welcome"]:

            return



        name = getattr(
            user,
            "first_name",
            "دوست عزیز"
        )


        await event.reply(

f"""
🌟 ربات مدیریت گروه FPS 🌟


سلام {name} عزیز 👋


به گروه خوش آمدید 🌹


📚 برای راهنما بنویسید:

راهنما


🔥 FPS Manager

"""

        )



    except Exception:


        traceback.print_exc()







# ===============================
# START
# ===============================


def start_bot():


    print(
        "🌟 FPS Group Manager Started"
    )


    try:


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






# ===============================
# RUN
# ===============================


if __name__ == "__main__":


    start_bot()