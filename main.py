# =========================================
# FPS Manager Ultimate v4
# Part 1/6
# =========================================

import os
import json
import time
import random
import traceback

from datetime import datetime
from collections import defaultdict
from zoneinfo import ZoneInfo

from splusthon import SoroushClient
from splusthon import events


# ===============================
# CONFIG
# ===============================

SESSION_NAME = "splus_manager.session"

DATABASE = "fps_database.json"

OWNER_ID = "68244916"

BOT_NAME = "🌟 ربات مدیریت گروه FPS 🌟"

BOT_LINK = "https://splus.ir/FPS_BOT"



client = SoroushClient(
    SESSION_NAME
)



# ===============================
# TIME
# ===============================

def iran_time():

    return datetime.now(
        ZoneInfo("Asia/Tehran")
    )



def clock():

    return iran_time().strftime(
        "%H:%M:%S"
    )



def date():

    return iran_time().strftime(
        "%Y/%m/%d"
    )



def time_box():

    return f"""
🕒 ساعت:
{clock()}

📅 تاریخ:
{date()}
"""



# ===============================
# DEFAULT SETTINGS
# ===============================

DEFAULT_GROUP = {

    # امنیت

    "anti_link": True,

    "anti_spam": True,

    "filter": True,

    "auto_ban": True,


    # هوش مصنوعی

    "speaker": True,

    "talkative": False,

    "quiet": True,


    # اعضا

    "welcome": True,

    "goodbye": True,


    # چالش

    "challenge": True,


    # فیلتر

    "filters": []

}





DEFAULT_DATABASE = {


    "users": {},


    "groups": {},


    "owners": {},


    "admins": {},


    "warnings": {},


    "banned": {},


    "muted": {},


    "messages": {},


    "challenge_used": {},


    "started": int(time.time())

}





# ===============================
# LOAD / SAVE DATABASE
# ===============================


def save_db():

    try:

        with open(
            DATABASE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                db,
                file,
                ensure_ascii=False,
                indent=4
            )


    except Exception:

        traceback.print_exc()





def load_db():

    if not os.path.exists(
        DATABASE
    ):

        return DEFAULT_DATABASE.copy()



    try:

        with open(
            DATABASE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)



        for key,value in DEFAULT_DATABASE.items():

            if key not in data:

                data[key] = value



        return data



    except Exception:

        return DEFAULT_DATABASE.copy()




db = load_db()





# ===============================
# GROUP SYSTEM
# ===============================


def init_group(group_id):

    gid = str(group_id)



    if gid not in db["groups"]:


        db["groups"][gid] = DEFAULT_GROUP.copy()


        db["owners"][gid] = None


        db["admins"][gid] = []


        db["warnings"][gid] = {}


        db["banned"][gid] = []


        db["muted"][gid] = {}



        save_db()



    else:


        changed = False


        for key,value in DEFAULT_GROUP.items():

            if key not in db["groups"][gid]:

                db["groups"][gid][key] = value

                changed = True



        if changed:

            save_db()





def get_group(group_id):

    init_group(
        group_id
    )

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
# FPS Manager Ultimate v4
# Part 2/6
# =========================================



# ===============================
# OWNER SYSTEM
# ===============================


def set_owner(
        group_id,
        user_id
):

    gid = str(group_id)


    init_group(
        group_id
    )


    if db["owners"][gid] is None:


        db["owners"][gid] = str(user_id)

        save_db()

        return True



    return False





def get_owner(
        group_id
):

    return db["owners"].get(
        str(group_id)
    )





def is_owner(
        group_id,
        user_id
):

    return str(user_id) == str(
        get_owner(group_id)
    )





# ===============================
# ADMIN SYSTEM
# ===============================


def add_admin(
        group_id,
        user_id
):

    gid = str(group_id)

    uid = str(user_id)


    init_group(
        group_id
    )



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



    if uid in db["admins"].get(gid,[]):

        db["admins"][gid].remove(uid)

        save_db()

        return True



    return False





def is_admin(
        group_id,
        user_id
):

    uid = str(user_id)


    if is_owner(
        group_id,
        user_id
    ):

        return True



    return uid in db["admins"].get(
        str(group_id),
        []
    )





# ===============================
# BOT PERMISSION CHECK
# ===============================


async def bot_is_admin(event):

    """
    بررسی اینکه ربات داخل گروه مدیر هست یا نه
    """

    try:


        me = await event.client.get_me()


        permission = await event.client.get_permissions(
            await event.get_chat(),
            me
        )


        return bool(
            permission.is_admin
        )



    except Exception:


        return False





# ===============================
# WARNING SYSTEM
# ===============================


MAX_WARN = 3





def add_warning(
        group_id,
        user_id
):

    gid = str(group_id)

    uid = str(user_id)



    if uid not in db["warnings"][gid]:

        db["warnings"][gid][uid] = 0



    db["warnings"][gid][uid] += 1


    save_db()


    return db["warnings"][gid][uid]





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





def clear_warning(
        group_id,
        user_id
):

    gid = str(group_id)

    uid = str(user_id)



    if uid in db["warnings"][gid]:

        del db["warnings"][gid][uid]

        save_db()

        return True



    return False





# ===============================
# BAN SYSTEM
# ===============================


def add_ban(
        group_id,
        user_id
):

    gid = str(group_id)

    uid = str(user_id)



    if uid not in db["banned"][gid]:

        db["banned"][gid].append(uid)

        save_db()

        return True



    return False





def remove_ban(
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


    db["muted"][gid][uid] = {

        "start": time.time(),

        "time": minutes * 60

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



    if time.time() - data["start"] >= data["time"]:


        del db["muted"][gid][uid]

        save_db()

        return False



    return True# =========================================
# FPS Manager Ultimate v4
# Part 3/6
# =========================================


# ===============================
# SMART TALK
# ===============================


PUBLIC_WORDS = {

    "سلام": [
        "سلام 👋🌟",
        "سلام رفیق 🔥"
    ],

    "درود": [
        "درود بر شما 🌹"
    ],

    "ارادت": [
        "ارادت 🤝"
    ],

    "صبح بخیر": [
        "صبح شما بخیر ☀️"
    ],

    "شب بخیر": [
        "شب شما بخیر 🌙"
    ]

}



REPLY_WORDS = {

    "چطوری": [
        "خوبم 😎 آماده خدمت هستم",
        "عالی‌ام 🤖"
    ],

    "کی هستی": [
        "من ربات مدیریت گروه FPS هستم 🤖"
    ],

    "چه کاره‌ای": [
        "برای مدیریت گروه و کمک به اعضا ساخته شدم 🛡"
    ],

    "اسمت چیه": [
        "FPS Manager 🌟"
    ]

}





def is_reply(event):

    try:

        return bool(
            event.reply_to_msg_id
        )

    except:

        return False





def smart_reply(
        text,
        group_id,
        event
):


    group = get_group(
        group_id
    )



    if not group.get(
        "speaker",
        True
    ):

        return None



    text = text.lower()



    # حالت کم حرفی

    if group.get(
        "quiet",
        False
    ):

        if not is_reply(event):

            for word in PUBLIC_WORDS:

                if word in text:

                    return random.choice(
                        PUBLIC_WORDS[word]
                    )


            return None




    # جواب‌های عمومی


    for word in PUBLIC_WORDS:


        if word in text:


            return random.choice(
                PUBLIC_WORDS[word]
            )





    # جواب فقط با ریپلای


    if is_reply(event):


        for word in REPLY_WORDS:


            if word in text:


                return random.choice(
                    REPLY_WORDS[word]
                )



    return None





# ===============================
# CHALLENGE SYSTEM
# ===============================


CHALLENGES = [

"از چه چیزی خوشت میاد؟",

"از چه چیزی بدت میاد؟",

"بهترین خاطره‌ات چیست؟",

"اگر یک قدرت داشتی چه انتخاب می‌کردی؟",

"بهترین بازی که انجام دادی چیست؟",

"دوست داری کجا سفر کنی؟",

"یک آرزوی بزرگ داری؟",

"اگر معروف می‌شدی چه کاری می‌کردی؟",

"بهترین دوستت چه ویژگی دارد؟",

"چه چیزی تو را خوشحال می‌کند؟",

"آخرین فیلمی که دیدی چه بود؟",

"اگر یک روز نامرئی بودی چه می‌کردی؟"

]





def get_challenge(
        user_id
):


    uid = str(user_id)


    if uid not in db["challenge_used"]:

        db["challenge_used"][uid] = []



    used = db["challenge_used"][uid]



    available = [

        i for i in range(
            len(CHALLENGES)
        )

        if i not in used

    ]



    if not available:


        db["challenge_used"][uid] = []

        available = list(
            range(
                len(CHALLENGES)
            )
        )



    pick = random.choice(
        available
    )


    db["challenge_used"][uid].append(
        pick
    )


    save_db()



    return (
        pick + 1,
        CHALLENGES[pick]
    )





# ===============================
# PROFILE
# ===============================


def profile(
        user_id
):

    uid = str(user_id)


    user = db["users"].get(
        uid,
        {}
    )



    return f"""
👤 پروفایل FPS

🏷 نام:
{user.get("name","کاربر")}


💬 پیام‌ها:
{db["messages"].get(uid,0)}


📅 ورود:
{datetime.fromtimestamp(
user.get("join",time.time())
).strftime("%Y/%m/%d")}


⚠️ مجموع اخطار:
{sum(
    db["warnings"].get(g,{}).get(uid,0)
    for g in db["warnings"]
)}
"""





# ===============================
# BOT INFO
# ===============================


def active_text(
        owner_name="نامشخص",
        owner_id="نامشخص"
):

    return f"""
✅ ربات فعال است!


👑 مالک گروه:
{owner_name}

🆔 آیدی:
{owner_id}


🔹 فقط مالک گروه می‌تواند ربات را مدیریت کند.

🔹 برای مشاهده دستورات:
راهنما


📌 {BOT_LINK}
"""# =========================================
# FPS Manager Ultimate v4
# Part 4/6
# =========================================



# ===============================
# HELP
# ===============================


def help_text():

    return """
🌟 ربات مدیریت گروه FPS 🌟


📚 دستورات عمومی:

راهنما
فعال
پروفایل
چالش
زمان


⚙️ تنظیمات (فقط مدیر):

سخنگو روشن
سخنگو خاموش

خوشامدگویی روشن
خوشامدگویی خاموش

خداحافظی روشن
خداحافظی خاموش

پرحرفی روشن
پرحرفی خاموش

کم حرفی روشن
کم حرفی خاموش



🛡 مدیریت:

اخطار (با ریپلای)
پاک کردن اخطار (با ریپلای)

بن (با ریپلای)
آنبن (با ریپلای)


👑 مالک:

پنل ادمین
"""
    





# ===============================
# OWNER PANEL
# ===============================


def owner_panel():

    return """
👑 پنل مدیریت FPS


📊 آمار ربات

👥 کاربران

📂 گروه‌ها

📢 پیام همگانی


⚙️ تنظیمات گروه:

سخنگو روشن/خاموش

خوشامدگویی روشن/خاموش

خداحافظی روشن/خاموش

پرحرفی روشن/خاموش

کم حرفی روشن/خاموش
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


💬 پیام‌ها:
{sum(db["messages"].values())}


⏰ اجرا از:
{datetime.fromtimestamp(
db["started"]
).strftime("%Y/%m/%d %H:%M")}
"""





# ===============================
# SETTINGS
# ===============================


async def set_group_setting(
        event,
        group_id,
        user_id,
        text
):


    if not is_admin(
        group_id,
        user_id
    ):

        return False




    group = get_group(
        group_id
    )



    options = {


        "سخنگو روشن":
        ("speaker",True),


        "سخنگو خاموش":
        ("speaker",False),



        "خوشامدگویی روشن":
        ("welcome",True),


        "خوشامدگویی خاموش":
        ("welcome",False),



        "خداحافظی روشن":
        ("goodbye",True),


        "خداحافظی خاموش":
        ("goodbye",False),



        "پرحرفی روشن":
        ("talkative",True),


        "پرحرفی خاموش":
        ("talkative",False),



        "کم حرفی روشن":
        ("quiet",True),


        "کم حرفی خاموش":
        ("quiet",False)

    }




    if text not in options:

        return False



    key,value = options[text]



    group[key] = value


    save_db()



    await event.reply(
f"""
✅ تنظیم شد

⚙️ {text}
"""
    )


    return True





# ===============================
# REPLY USER
# ===============================


async def reply_user(
        event
):

    try:

        msg = await event.get_reply_message()


        if not msg:

            return None



        return msg.sender_id



    except:

        return None





# ===============================
# WARNING COMMAND
# ===============================


async def warning_command(
        event,
        group_id,
        user_id
):


    if not is_admin(
        group_id,
        user_id
    ):

        await event.reply(
"❌ فقط مدیرها اجازه دارند."
        )

        return True



    target = await reply_user(
        event
    )



    if not target:

        await event.reply(
"⚠️ روی پیام کاربر ریپلای کنید."
        )

        return True




    if is_owner(
        group_id,
        target
    ):

        await event.reply(
"❌ مالک گروه قابل اخطار نیست."
        )

        return True




    count = add_warning(
        group_id,
        target
    )



    await event.reply(
f"""
⚠️ اخطار ثبت شد

🔢 تعداد:
{count}/3
"""
    )



    return True# =========================================
# FPS Manager Ultimate v4
# Part 5/6
# =========================================



# ===============================
# LINK CHECK
# ===============================


def contains_link(text):

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
# SPAM SYSTEM
# ===============================


spam = defaultdict(list)



def spam_check(
        user_id
):

    uid = str(user_id)

    now = time.time()



    spam[uid] = [

        x for x in spam[uid]

        if now - x < 10

    ]



    spam[uid].append(
        now
    )



    if len(spam[uid]) >= 8:

        return True



    return False





# ===============================
# AUTO WARNING
# ===============================


async def auto_warn(
        event,
        group_id,
        user_id,
        reason
):


    # اگر ربات مدیر نیست کاری نکند


    if not await bot_is_admin(
        event
    ):

        return False



    count = add_warning(
        group_id,
        user_id
    )



    await event.reply(
f"""
⚠️ اخطار خودکار

📌 دلیل:
{reason}

🔢 اخطار:
{count}/3
"""
    )



    if count >= MAX_WARN:


        if get_group(group_id).get(
            "auto_ban",
            True
        ):


            add_ban(
                group_id,
                user_id
            )


            await event.reply(
"""
🚫 کاربر به دلیل ۳ اخطار بن شد.
"""
            )



    return True





# ===============================
# JOIN / LEFT
# ===============================


@client.on(events.ChatAction)
async def join_leave(event):


    try:


        chat = await event.get_chat()


        group_id = chat.id



        init_group(
            group_id
        )



        group = get_group(
            group_id
        )



        user = await event.get_user()



        name = getattr(
            user,
            "first_name",
            "کاربر"
        )



        if event.user_joined or event.user_added:


            if group["welcome"]:


                await event.reply(
f"""
👋 خوش آمدی {name}


🌟 FPS Manager
{time_box()}
"""
                )





        if event.user_left or event.user_kicked:


            if group["goodbye"]:


                await event.reply(
f"""
👋 {name} گروه را ترک کرد.

{time_box()}
"""
                )



    except Exception:


        traceback.print_exc()





# ===============================
# MESSAGE EVENT
# ===============================


@client.on(events.NewMessage)
async def main_handler(event):


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



        group_id = chat.id



        # اگر گروه بود


        if getattr(
            chat,
            "megagroup",
            False
        ):


            init_group(
                group_id
            )



            if not get_owner(
                group_id
            ):

                set_owner(
                    group_id,
                    user_id
                )




            # بن شده


            if is_banned(
                group_id,
                user_id
            ):

                return




            group = get_group(
                group_id
            )




            # ضد لینک


            if group["anti_link"]:

                if contains_link(text):


                    if not is_admin(
                        group_id,
                        user_id
                    ):


                        await auto_warn(
                            event,
                            group_id,
                            user_id,
                            "ارسال لینک"
                        )


                        return






            # ضد اسپم


            if group["anti_spam"]:


                if spam_check(
                    user_id
                ):


                    await auto_warn(
                        event,
                        group_id,
                        user_id,
                        "اسپم"
                    )


                    return





        # تنظیمات


        if getattr(
            chat,
            "megagroup",
            False
        ):


            if await set_group_setting(
                event,
                group_id,
                user_id,
                text
            ):

                return





        # دستورات


        if text in [
            "راهنما",
            "کمک"
        ]:

            await event.reply(
                help_text()
            )

            return



        if text == "فعال":


            owner = get_owner(
                group_id
            )


            await event.reply(
                active_text(
                    "مالک گروه",
                    owner
                )
            )


            return





        if text == "چالش":


            num,q = get_challenge(
                user_id
            )


            await event.reply(
f"""
🎯 چالش

🔢 شماره:
{num}

❓ سوال:
{q}
"""
            )


            return





        if text == "پروفایل":


            await event.reply(
                profile(
                    user_id
                )
            )


            return





        # سخنگو


        if getattr(
            chat,
            "megagroup",
            False
        ):


            answer = smart_reply(
                text,
                group_id,
                event
            )


            if answer:


                await event.reply(
                    answer
                )



    except Exception:


        traceback.print_exc()# =========================================
# FPS Manager Ultimate v4
# Part 6/6
# =========================================



# ===============================
# ADMIN COMMANDS
# ===============================


async def ban_command(
        event,
        group_id,
        user_id
):


    if not is_admin(
        group_id,
        user_id
    ):

        await event.reply(
            "❌ دسترسی ندارید."
        )

        return



    target = await reply_user(
        event
    )


    if not target:

        await event.reply(
            "⚠️ روی پیام کاربر ریپلای کنید."
        )

        return



    if is_owner(
        group_id,
        target
    ):

        await event.reply(
            "❌ مالک گروه قابل بن نیست."
        )

        return



    add_ban(
        group_id,
        target
    )


    await event.reply(
        "🚫 کاربر بن شد."
    )





async def unban_command(
        event,
        group_id,
        user_id
):


    if not is_admin(
        group_id,
        user_id
    ):

        return



    target = await reply_user(
        event
    )


    if target:


        remove_ban(
            group_id,
            target
        )


        await event.reply(
            "✅ کاربر از بن خارج شد."
        )





async def clear_warning_command(
        event,
        group_id,
        user_id
):


    if not is_admin(
        group_id,
        user_id
    ):

        return



    target = await reply_user(
        event
    )


    if target:

        clear_warning(
            group_id,
            target
        )


        await event.reply(
            "✅ اخطارها پاک شد."
        )





# ===============================
# OWNER PANEL COMMAND
# ===============================


@client.on(events.NewMessage(pattern="پنل ادمین"))
async def owner_panel_command(event):


    try:


        sender = await event.get_sender()


        if str(sender.id) != OWNER_ID:


            await event.reply(
                "❌ فقط سازنده ربات."
            )

            return



        await event.reply(
            owner_panel()
        )


    except Exception:

        traceback.print_exc()





# ===============================
# MANAGEMENT COMMAND CONNECT
# ===============================


@client.on(events.NewMessage(pattern="اخطار"))
async def warning_handler(event):


    try:

        chat = await event.get_chat()


        if not getattr(
            chat,
            "megagroup",
            False
        ):

            return



        sender = await event.get_sender()


        await warning_command(
            event,
            chat.id,
            sender.id
        )


    except Exception:

        traceback.print_exc()





@client.on(events.NewMessage(pattern="بن"))
async def ban_handler(event):


    try:

        chat = await event.get_chat()


        if not getattr(
            chat,
            "megagroup",
            False
        ):

            return



        sender = await event.get_sender()


        await ban_command(
            event,
            chat.id,
            sender.id
        )


    except Exception:

        traceback.print_exc()





@client.on(events.NewMessage(pattern="آنبن"))
async def unban_handler(event):


    try:

        chat = await event.get_chat()


        sender = await event.get_sender()


        await unban_command(
            event,
            chat.id,
            sender.id
        )


    except Exception:

        traceback.print_exc()





# ===============================
# START
# ===============================


def run():

    print(
        "🌟 FPS Manager Ultimate v4 Started 🌟"
    )


    try:


        client.start()


        print(
            "✅ Bot Online"
        )


        client.run_until_disconnected()



    except Exception:


        traceback.print_exc()





if __name__ == "__main__":

    run()
