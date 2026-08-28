# =========================================
# 🌟 FPS Manager Ultimate v3 🌟
# Part 1/6
# =========================================

import os
import json
import time
import random
import asyncio
import traceback

from datetime import datetime
from collections import defaultdict
from zoneinfo import ZoneInfo

from splusthon import SoroushClient
from splusthon import events



# ===============================
# CONFIG
# ===============================

SESSION = "splus_manager.session"

DB_FILE = "fps_database.json"

OWNER_ID = "68244916"

BOT_LINK = "https://splus.ir/FPS_BOT"

BOT_NAME = "🌟 ربات مدیریت گروه FPS 🌟"



client = SoroushClient(
    SESSION
)



# ===============================
# TIME SYSTEM
# ===============================


def iran_now():

    return datetime.now(
        ZoneInfo("Asia/Tehran")
    )



def get_time():

    return iran_now().strftime(
        "%H:%M:%S"
    )



def get_date():

    return iran_now().strftime(
        "%Y/%m/%d"
    )



def full_time():

    return f"""
🕒 ساعت:
{get_time()}

📅 تاریخ:
{get_date()}
"""



# ===============================
# DEFAULT GROUP SETTINGS
# ===============================


DEFAULT_GROUP = {


    # امنیت

    "anti_link": True,

    "anti_spam": True,

    "filter": True,


    # مدیریت

    "auto_ban": True,


    # هوشمند

    "speak": True,

    "talkative": False,

    "quiet": True,


    # اعضا

    "welcome": True,

    "goodbye": True,


    # قوانین

    "rules": "📜 هنوز قانونی ثبت نشده است",


    # فیلتر

    "filters": []

}





DEFAULT_DB = {


    "users": {},


    "groups": {},


    "admins": {},


    "owners": {},


    "warnings": {},


    "banned": {},


    "muted": {},


    "messages": {},


    "challenge_history": {},


    "bot_start": int(time.time())

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
# GROUP INIT
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


        changed = False


        for key,value in DEFAULT_GROUP.items():

            if key not in db["groups"][gid]:

                db["groups"][gid][key] = value

                changed = True



        if changed:

            save_db()




def get_group(group_id):

    init_group(group_id)

    return db["groups"][str(group_id)]




# ===============================
# USER SYSTEM
# ===============================


def save_user(user_id,name):

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
# 🌟 FPS Manager Ultimate v3 🌟
# Part 2/6
# =========================================


# ===============================
# OWNER SYSTEM
# ===============================


def set_owner(group_id,user_id):

    gid = str(group_id)

    init_group(group_id)


    if db["owners"][gid] is None:

        db["owners"][gid] = str(user_id)

        save_db()

        return True


    return False




def get_owner(group_id):

    return db["owners"].get(
        str(group_id),
        None
    )




def is_owner(group_id,user_id):

    return str(user_id) == str(
        get_owner(group_id)
    )




# ===============================
# ADMIN SYSTEM
# ===============================


def is_admin(group_id,user_id):

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
# BOT ADMIN CHECK
# ===============================


async def bot_has_admin(event):

    """
    بررسی دسترسی ربات در گروه
    اگر ربات مدیر نباشد:
    هیچ اخطار/بن خودکاری انجام نمی‌شود
    """

    try:

        permissions = await event.client.get_permissions(
            await event.get_chat(),
            "me"
        )


        if permissions and permissions.is_admin:

            return True



        return False



    except Exception:


        return False





# ===============================
# WARNING SYSTEM
# ===============================


MAX_WARNING = 3





def add_warning(group_id,user_id):

    gid = str(group_id)

    uid = str(user_id)



    if uid not in db["warnings"][gid]:

        db["warnings"][gid][uid] = 0



    db["warnings"][gid][uid] += 1


    save_db()


    return db["warnings"][gid][uid]





def get_warning(group_id,user_id):

    return db["warnings"].get(
        str(group_id),
        {}
    ).get(
        str(user_id),
        0
    )





def clear_warning(group_id,user_id):

    gid = str(group_id)

    uid = str(user_id)



    if uid in db["warnings"][gid]:

        del db["warnings"][gid][uid]

        save_db()

        return True



    return False





# ===============================
# AUTO BAN CHECK
# ===============================


def can_auto_ban(group_id):

    return get_group(group_id).get(
        "auto_ban",
        False
    )





# ===============================
# BAN DATABASE
# ===============================


def add_ban(group_id,user_id):

    gid = str(group_id)

    uid = str(user_id)



    if uid not in db["banned"][gid]:

        db["banned"][gid].append(uid)

        save_db()

        return True



    return False




def remove_ban(group_id,user_id):

    gid = str(group_id)

    uid = str(user_id)



    if uid in db["banned"][gid]:

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


def add_mute(group_id,user_id,minutes):

    gid = str(group_id)

    uid = str(user_id)



    db["muted"][gid][uid] = {

        "time": int(time.time()),

        "duration": minutes * 60

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



    if time.time() - data["time"] >= data["duration"]:

        del db["muted"][gid][uid]

        save_db()

        return False



    return True




def remove_mute(group_id,user_id):

    gid = str(group_id)

    uid = str(user_id)


    if uid in db["muted"].get(gid,{}):

        del db["muted"][gid][uid]

        save_db()

        return True


    return False# =========================================
# 🌟 FPS Manager Ultimate v3 🌟
# Part 3/6
# =========================================


# ===============================
# SMART TALK SYSTEM
# ===============================


NORMAL_WORDS = {

    "سلام":[
        "سلام 👋🌟",
        "سلام عزیز، خوش آمدی 🔥"
    ],

    "درود":[
        "درود بر شما 🌹"
    ],

    "ارادت":[
        "ارادت متقابل 🤝🔥"
    ],

    "صبح بخیر":[
        "صبح شما هم بخیر ☀️"
    ],

    "شب بخیر":[
        "شب شما هم بخیر 🌙"
    ]

}



REPLY_WORDS = {

    "چطوری":[
        "عالی‌ام 🤖 آماده خدمت هستم",
        "خوبم، ممنون که پرسیدی 😎"
    ],

    "کی هستی":[
        "من 🌟 ربات مدیریت گروه FPS هستم"
    ],

    "چه کاره‌ای":[
        "کار من کمک به مدیریت گروه‌هاست 🛡"
    ],

    "اسمت چیه":[
        "FPS Manager 🤖"
    ]

}




def is_reply_to_bot(event):

    try:

        reply = event.reply_to_msg_id

        if reply:

            return True


        return False


    except Exception:

        return False





def smart_answer(text,group_id,event):

    group = get_group(group_id)


    if not group.get(
        "speak",
        True
    ):

        return None



    text = text.lower().strip()



    # سلام‌ها همیشه آزاد


    for word,answers in NORMAL_WORDS.items():

        if word in text:

            return random.choice(
                answers
            )



    # سوال‌ها فقط با ریپلای


    if not is_reply_to_bot(event):

        return None



    for word,answers in REPLY_WORDS.items():

        if word in text:

            return random.choice(
                answers
            )



    # حالت پرحرفی


    if group.get(
        "talkative",
        False
    ):


        extra = [

            "🔥",

            "😎",

            "🤖"

        ]


        if len(text) > 3:

            return random.choice(extra)



    return None





# ===============================
# CHALLENGE SYSTEM
# ===============================


CHALLENGES = [

"از چه چیزی خوشت میاد؟",

"از چه چیزی بدت میاد؟",

"بهترین خاطره‌ات چیه؟",

"اگر یک قدرت داشتی چی انتخاب می‌کردی؟",

"دوست داری کجا سفر کنی؟",

"بهترین بازی که انجام دادی چی بوده؟",

"بزرگ‌ترین هدف تو چیه؟",

"اگر مدیر گروه بودی چه قانونی می‌گذاشتی؟",

"یک استعداد مخفی داری؟",

"آخرین چیزی که خوشحالت کرد چی بود؟",

]





def get_challenge(user_id):

    uid = str(user_id)


    if uid not in db["challenge_history"]:

        db["challenge_history"][uid] = []



    used = db["challenge_history"][uid]



    available = [

        i for i in range(
            len(CHALLENGES)
        )

        if i not in used

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


    return number+1, CHALLENGES[number]





# ===============================
# PROFILE
# ===============================


def user_profile(user_id):

    uid = str(user_id)


    user = db["users"].get(
        uid,
        {}
    )


    return f"""
👤 پروفایل FPS

🏷 نام:
{user.get("name","کاربر")}

💬 تعداد پیام:
{db["messages"].get(uid,0)}

📅 ورود:
{datetime.fromtimestamp(
user.get("join",time.time())
).strftime("%Y/%m/%d")}

⚠️ اخطار:
{sum(
db["warnings"].get(
g,
{}
).get(
uid,
0
)
for g in db["warnings"]
)}
"""





# ===============================
# WELCOME / GOODBYE
# ===============================


def welcome_message(name):

    return f"""
🌟 ربات مدیریت گروه FPS 🌟

👋 سلام {name}

به گروه خوش آمدید 🌹
"""




def goodbye_message(name):

    return f"""
👋 {name} گروه را ترک کرد.

{full_time()}
"""# =========================================
# 🌟 FPS Manager Ultimate v3 🌟
# Part 4/6
# =========================================


# ===============================
# ANTI LINK
# ===============================


def has_link(text):

    links = [

        "http://",
        "https://",
        "www.",
        ".com",
        ".ir"

    ]


    text = text.lower()


    for x in links:

        if x in text:

            return True


    return False





# ===============================
# ANTI SPAM
# ===============================


spam_list = defaultdict(list)



def is_spam(user_id):

    now = time.time()


    uid = str(user_id)


    spam_list[uid] = [

        x for x in spam_list[uid]

        if now - x < 10

    ]


    spam_list[uid].append(now)



    if len(spam_list[uid]) >= 7:

        return True



    return False





# ===============================
# FILTER WORD
# ===============================


def has_bad_word(group_id,text):

    filters = get_group(
        group_id
    ).get(
        "filters",
        []
    )


    for word in filters:

        if word in text:

            return True


    return False





# ===============================
# AUTO WARNING CHECK
# ===============================


async def auto_warning(
        event,
        group_id,
        user_id,
        reason
):


    # اول بررسی ربات


    if not await bot_has_admin(event):

        return False



    count = add_warning(
        group_id,
        user_id
    )



    await event.reply(
f"""
⚠️ اخطار ثبت شد

📌 دلیل:
{reason}

🔢 تعداد اخطار:
{count}/3
"""
    )



    if count >= 3:


        if can_auto_ban(
            group_id
        ):


            add_ban(
                group_id,
                user_id
            )


            await event.reply(
"""
🚫 کاربر به دلیل دریافت ۳ اخطار مسدود شد.
"""
            )



    return True





# ===============================
# GROUP SETTINGS
# ===============================


async def change_setting(
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



    settings = {


        "سخنگو روشن":
            ("speak",True),

        "سخنگو خاموش":
            ("speak",False),


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
            ("quiet",False),

    }




    if text in settings:


        key,value = settings[text]


        group[key] = value


        save_db()



        await event.reply(
f"""
✅ تنظیمات تغییر کرد

⚙️ {text}
"""
        )


        return True



    return False





# ===============================
# SETTINGS LIST
# ===============================


def settings_help():

    return """
⚙️ تنظیم قابلیت‌های ربات


🔹 سخنگو روشن / خاموش

🔹 خوشامدگویی روشن / خاموش

🔹 خداحافظی روشن / خاموش

🔹 پرحرفی روشن / خاموش

🔹 کم حرفی روشن / خاموش
"""# =========================================
# 🌟 FPS Manager Ultimate v3 🌟
# Part 5/6
# =========================================



# ===============================
# OWNER PANEL
# ===============================


def admin_panel():

    return """
👑 پنل مدیریت FPS


📊 آمار

👥 تعداد کاربران

📂 تعداد گروه‌ها

📢 پیام همگانی

💾 ذخیره اطلاعات


⚙️ تنظیمات:

سخنگو روشن/خاموش

خوشامدگویی روشن/خاموش

خداحافظی روشن/خاموش

پرحرفی روشن/خاموش

کم حرفی روشن/خاموش
"""





# ===============================
# STATS
# ===============================


def get_stats():

    return f"""
📊 آمار ربات


👥 کاربران:
{len(db["users"])}


📂 گروه‌ها:
{len(db["groups"])}


💬 پیام‌ها:
{sum(db["messages"].values())}


⏰ زمان شروع:

{datetime.fromtimestamp(
db["bot_start"]
).strftime("%Y/%m/%d %H:%M")}
"""





# ===============================
# REPLY USER FINDER
# ===============================


async def get_reply_user(event):

    try:

        msg = await event.get_reply_message()


        if not msg:

            return None



        return msg.sender_id



    except Exception:

        return None





# ===============================
# MANUAL WARNING
# ===============================


async def warn_command(
        event,
        group_id,
        user_id
):


    if not is_admin(
        group_id,
        user_id
    ):

        await event.reply(
"""
❌ شما اجازه اخطار دادن ندارید.
"""
        )

        return True



    target = await get_reply_user(
        event
    )



    if not target:

        await event.reply(
"""
⚠️ روی پیام کاربر ریپلای کنید.
"""
        )

        return True



    if is_owner(
        group_id,
        target
    ):


        await event.reply(
"""
❌ نمی‌توانید مالک گروه را اخطار دهید.
"""
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


    return True





# ===============================
# CLEAR WARNING
# ===============================


async def clear_warn_command(
        event,
        group_id,
        user_id
):


    if not is_admin(
        group_id,
        user_id
    ):

        return True



    target = await get_reply_user(
        event
    )


    if target:

        clear_warning(
            group_id,
            target
        )


        await event.reply(
"""
✅ اخطارهای کاربر پاک شد.
"""
        )


    return True





# ===============================
# BAN COMMAND
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

        return True



    target = await get_reply_user(
        event
    )


    if not target:

        await event.reply(
"""
⚠️ روی پیام کاربر ریپلای کنید.
"""
        )

        return True



    if is_owner(
        group_id,
        target
    ):

        await event.reply(
"""
❌ مالک قابل بن نیست.
"""
        )

        return True



    add_ban(
        group_id,
        target
    )


    await event.reply(
"""
🚫 کاربر به لیست بن اضافه شد.
"""
    )


    return True





# ===============================
# UNBAN
# ===============================


async def unban_command(
        event,
        group_id,
        user_id
):


    if not is_admin(
        group_id,
        user_id
    ):

        return True



    target = await get_reply_user(
        event
    )


    if target:

        remove_ban(
            group_id,
            target
        )


        await event.reply(
"""
✅ کاربر از بن خارج شد.
"""
        )


    return True# =========================================
# 🌟 FPS Manager Ultimate v3 🌟
# Part 6/6
# =========================================


# ===============================
# USER JOIN / LEFT
# ===============================


@client.on(events.ChatAction)
async def member_events(event):

    try:

        chat = await event.get_chat()

        group_id = chat.id


        init_group(
            group_id
        )


        # ورود


        if event.user_joined or event.user_added:


            if not get_group(group_id).get(
                "welcome",
                True
            ):

                return



            user = await event.get_user()


            name = getattr(
                user,
                "first_name",
                "کاربر"
            )


            await event.reply(
                welcome_message(name)
            )



        # خروج


        if event.user_left or event.user_kicked:


            if not get_group(group_id).get(
                "goodbye",
                True
            ):

                return



            user = await event.get_user()


            name = getattr(
                user,
                "first_name",
                "کاربر"
            )


            await event.reply(
                goodbye_message(name)
            )


    except Exception:

        traceback.print_exc()





# ===============================
# MAIN MESSAGE
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



            if text == "پنل ادمین":


                if str(user_id) == OWNER_ID:


                    await event.reply(
                        admin_panel()
                    )

                else:

                    await event.reply(
                        "❌ دسترسی ندارید"
                    )



            return





        group_id = chat.id


        init_group(
            group_id
        )



        # ثبت مالک اولیه


        if not get_owner(group_id):

            set_owner(
                group_id,
                user_id
            )




        # ===========================
        # امنیت
        # ===========================


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


            if has_link(text):


                if not is_admin(
                    group_id,
                    user_id
                ):


                    await auto_warning(
                        event,
                        group_id,
                        user_id,
                        "ارسال لینک"
                    )


                    return





        # ضد اسپم


        if group["anti_spam"]:


            if is_spam(user_id):


                await auto_warning(
                    event,
                    group_id,
                    user_id,
                    "اسپم"
                )


                return





        # فیلتر


        if has_bad_word(
            group_id,
            text
        ):


            await auto_warning(
                event,
                group_id,
                user_id,
                "کلمه غیرمجاز"
            )


            return





        # ===========================
        # تنظیمات
        # ===========================


        if await change_setting(
            event,
            group_id,
            user_id,
            text
        ):

            return





        # ===========================
        # دستورات عمومی
        # ===========================


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

            return




        if text == "پروفایل":


            await event.reply(
                user_profile(user_id)
            )

            return





        if text == "تنظیمات":


            await event.reply(
                settings_help()
            )

            return





        # ===========================
        # سخنگو
        # ===========================


        answer = smart_answer(
            text,
            group_id,
            event
        )


        if answer:


            await event.reply(
                answer
            )



    except Exception:

        traceback.print_exc()





# ===============================
# START BOT
# ===============================


def start_bot():


    print(
        "🌟 FPS Manager Ultimate v3 Started 🌟"
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

    start_bot()
