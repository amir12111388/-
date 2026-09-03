# ===============================
# Anonymous Message Bot
# AMIR_FPS
# Part 1
# ===============================

import sqlite3
import random
import string

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)


# ===============================
# CONFIG
# ===============================

BOT_TOKEN = "8672916913:AAFGoB6vIijAfgggaFRO-rePf6SFoen4XYc"

OWNER_ID = 1382377947

BOT_NAME = "AMIR_FPS"


# ===============================
# DATABASE
# ===============================

db = sqlite3.connect(
    "bot.db",
    check_same_thread=False
)

cursor = db.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    banned INTEGER DEFAULT 0
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS links(
    code TEXT PRIMARY KEY,
    owner_id INTEGER
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS pending(
    user_id INTEGER PRIMARY KEY,
    owner_id INTEGER
)
""")


db.commit()



# ===============================
# DATABASE FUNCTIONS
# ===============================


def save_user(user):

    cursor.execute(
        """
        INSERT OR IGNORE INTO users
        (user_id, username, first_name, last_name)
        VALUES (?, ?, ?, ?)
        """,
        (
            user.id,
            user.username or "",
            user.first_name or "",
            user.last_name or ""
        )
    )

    db.commit()



def check_ban(user_id):

    cursor.execute(
        """
        SELECT banned
        FROM users
        WHERE user_id=?
        """,
        (user_id,)
    )

    result = cursor.fetchone()

    if result:
        return result[0] == 1

    return False



def create_link():

    code = "".join(
        random.choice(
            string.ascii_letters +
            string.digits
        )
        for _ in range(12)
    )


    cursor.execute(
        """
        INSERT INTO links
        VALUES (?,?)
        """,
        (
            code,
            OWNER_ID
        )
    )

    db.commit()

    return code



def get_link_owner(code):

    cursor.execute(
        """
        SELECT owner_id
        FROM links
        WHERE code=?
        """,
        (code,)
    )

    result = cursor.fetchone()

    if result:
        return result[0]

    return None



# ===============================
# START COMMAND
# ===============================


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    save_user(user)


    if check_ban(user.id):

        await update.message.reply_text(
            "🚫 شما از استفاده از ربات محروم شده‌اید."
        )

        return



    # صاحب ربات

    if user.id == OWNER_ID:

        keyboard = [
            [
                InlineKeyboardButton(
                    "🔗 دریافت لینک ناشناس",
                    callback_data="get_link"
                )
            ]
        ]


        await update.message.reply_text(
            f"سلام {BOT_NAME} 👋\n"
            "پنل شخصی شما فعال شد.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


        return



    # ورود با لینک

    if context.args:

        code = context.args[0]


        owner = get_link_owner(code)


        if owner == OWNER_ID:


            cursor.execute(
                """
                INSERT OR REPLACE INTO pending
                VALUES (?,?)
                """,
                (
                    user.id,
                    OWNER_ID
                )
            )

            db.commit()



            keyboard = [
                [
                    InlineKeyboardButton(
                        "❌ لغو",
                        callback_data="cancel"
                    )
                ]
            ]


            await update.message.reply_text(
                f"متن پیام ناشناسی که می‌خواهی برای {BOT_NAME} ارسال کنی را بفرست 👇",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

            return



    await update.message.reply_text(
        f"❌ این ربات مخصوص {BOT_NAME} ساخته شده است.\n"
        "شما توانایی استفاده از ربات را ندارید."
    )# ===============================
# Anonymous Message Bot
# AMIR_FPS
# Part 2
# ===============================


# ===============================
# BUTTON HANDLER
# ===============================


async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()


    user_id = query.from_user.id



    # ===========================
    # CREATE PERSONAL LINK
    # ===========================

    if query.data == "get_link":


        if user_id != OWNER_ID:
            return



        code = create_link()


        bot_info = await context.bot.get_me()


        link = (
            f"https://t.me/"
            f"{bot_info.username}"
            f"?start={code}"
        )


        await query.edit_message_text(
            "🔗 لینک ناشناس اختصاصی شما:\n\n"
            f"{link}\n\n"
            "این لینک را برای دریافت پیام ناشناس ارسال کنید."
        )



    # ===========================
    # CANCEL MESSAGE
    # ===========================

    elif query.data == "cancel":


        cursor.execute(
            """
            DELETE FROM pending
            WHERE user_id=?
            """,
            (user_id,)
        )

        db.commit()



        await query.edit_message_text(
            "❌ ارسال پیام لغو شد."
        )



    # ===========================
    # REPLY BUTTON
    # ===========================

    elif query.data.startswith("reply_"):


        if user_id != OWNER_ID:
            return



        target_id = int(
            query.data.replace(
                "reply_",
                ""
            )
        )


        context.user_data[
            "reply_user"
        ] = target_id



        await query.message.reply_text(
            "💬 پیام پاسخ را ارسال کنید:"
        )



    # ===========================
    # BAN BUTTON
    # ===========================

    elif query.data.startswith("ban_"):


        if user_id != OWNER_ID:
            return



        target_id = int(
            query.data.replace(
                "ban_",
                ""
            )
        )


        cursor.execute(
            """
            UPDATE users
            SET banned=1
            WHERE user_id=?
            """,
            (target_id,)
        )


        db.commit()



        await query.message.reply_text(
            "🚫 کاربر با موفقیت بن شد."
        )# ===============================
# Anonymous Message Bot
# AMIR_FPS
# Part 3
# ===============================


# ===============================
# MESSAGE HANDLER
# ===============================


async def message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    text = update.message.text



    # ===========================
    # CHECK BAN
    # ===========================

    if check_ban(user.id):
        return



    # ===========================
    # OWNER REPLY SYSTEM
    # ===========================

    if user.id == OWNER_ID:


        if "reply_user" in context.user_data:


            target = context.user_data[
                "reply_user"
            ]


            await context.bot.send_message(
                chat_id=target,
                text=(
                    f"💬 پاسخ از {BOT_NAME}:\n\n"
                    f"{text}"
                )
            )


            del context.user_data[
                "reply_user"
            ]



            await update.message.reply_text(
                "✅ پاسخ ارسال شد."
            )


            return



    # ===========================
    # FIND PENDING USER
    # ===========================


    cursor.execute(
        """
        SELECT owner_id
        FROM pending
        WHERE user_id=?
        """,
        (user.id,)
    )


    result = cursor.fetchone()



    if not result:


        await update.message.reply_text(
            "❌ ابتدا از لینک اختصاصی وارد شوید."
        )

        return



    owner_id = result[0]



    # ===========================
    # USER INFORMATION
    # ===========================


    username = (
        f"@{user.username}"
        if user.username
        else "ندارد"
    )


    first_name = (
        user.first_name
        if user.first_name
        else "-"
    )


    last_name = (
        user.last_name
        if user.last_name
        else "-"
    )



    message_text = (

        f"📩 پیام ناشناس جدید\n\n"

        f"👤 اطلاعات فرستنده:\n"
        f"نام: {first_name}\n"
        f"نام خانوادگی: {last_name}\n"
        f"یوزرنیم: {username}\n"
        f"آیدی عددی: {user.id}\n\n"

        f"💬 متن پیام:\n"
        f"{text}"
    )



    keyboard = [

        [

            InlineKeyboardButton(
                "💬 پاسخ",
                callback_data=f"reply_{user.id}"
            ),


            InlineKeyboardButton(
                "🚫 بن",
                callback_data=f"ban_{user.id}"
            )

        ]

    ]



    # ===========================
    # SEND TO OWNER
    # ===========================


    await context.bot.send_message(

        chat_id=owner_id,

        text=message_text,

        reply_markup=InlineKeyboardMarkup(
            keyboard
        )

    )



    # ===========================
    # DELETE PENDING
    # ===========================


    cursor.execute(
        """
        DELETE FROM pending
        WHERE user_id=?
        """,
        (user.id,)
    )


    db.commit()



    await update.message.reply_text(

        f"✅ پیام شما با موفقیت و به صورت ناشناس برای {BOT_NAME} ارسال شد."

    )# ===============================
# Anonymous Message Bot
# AMIR_FPS
# Part 4
# ===============================


# ===============================
# ERROR HANDLER
# ===============================


async def error_handler(
    update,
    context: ContextTypes.DEFAULT_TYPE
):

    print(
        "ERROR:",
        context.error
    )



# ===============================
# RUN BOT
# ===============================


def main():


    app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )



    # START

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )



    # BUTTONS

    app.add_handler(
        CallbackQueryHandler(
            button_handler
        )
    )



    # TEXT

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler
        )
    )



    # ERROR

    app.add_error_handler(
        error_handler
    )



    print(
        f"{BOT_NAME} Anonymous Bot Started..."
    )



    app.run_polling()




# ===============================
# START PROGRAM
# ===============================


if __name__ == "__main__":

    main()
