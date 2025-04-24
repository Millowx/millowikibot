import os
import json
import wikipediaapi
from flask import Flask, request
import telegram
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

app = Flask(__name__)
TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = telegram.Bot(token=TOKEN)

SUPPORTED_LANGUAGES = {
    "en": "English",
    "fa": "فارسی",
    "ar": "العربية",
    "ru": "Русский",
    "fr": "Français",
    "es": "Español",
    "de": "Deutsch",
    "zh": "中文",
    "ja": "日本語",
    "pt": "Português"
}

USER_LANG_FILE = "user_languages.json"
if not os.path.exists(USER_LANG_FILE):
    with open(USER_LANG_FILE, "w") as f:
        json.dump({}, f)

def load_user_langs():
    with open(USER_LANG_FILE, "r") as f:
        return json.load(f)

def save_user_langs(data):
    with open(USER_LANG_FILE, "w") as f:
        json.dump(data, f)

def get_user_lang(user_id):
    langs = load_user_langs()
    return langs.get(str(user_id), "en")

def set_user_lang(user_id, lang_code):
    langs = load_user_langs()
    langs[str(user_id)] = lang_code
    save_user_langs(langs)

def start(update, context):
    msg = "Please choose a language / لطفاً یک زبان انتخاب کنید:"
    keyboard = [[telegram.KeyboardButton(name)] for name in SUPPORTED_LANGUAGES.values()]
    reply_markup = telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text(msg, reply_markup=reply_markup)

def handle_message(update, context):
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    # اگر کاربر زبان انتخاب کرده
    for code, name in SUPPORTED_LANGUAGES.items():
        if text == name:
            set_user_lang(user_id, code)
            update.message.reply_text(f"Language set to {name}!")
            return

    lang = get_user_lang(user_id)

    # پیام برای کاربرانی که فقط آیدی بات رو تایپ می‌کنند
    if text.startswith("@"):
        credits_text = {
            "en": "Send Wikipedia links by this bot. cr: @MX_file",
            "fa": "لینک‌های ویکی‌پدیا را با این ربات ارسال کنید. cr: @MX_file",
            "ar": "أرسل روابط ويكيبيديا عبر هذا البوت. cr: @MX_file",
            "ru": "Отправляйте ссылки Википедии через этого бота. cr: @MX_file",
            "fr": "Envoyez des liens Wikipédia avec ce bot. cr: @MX_file",
            "es": "Envía enlaces de Wikipedia con este bot. cr: @MX_file",
            "de": "Sende Wikipedia-Links mit diesem Bot. cr: @MX_file",
            "zh": "通过此机器人发送维基百科链接。cr: @MX_file",
            "ja": "このボットでWikipediaのリンクを送信します。cr: @MX_file",
            "pt": "Envie links da Wikipédia com este bot. cr: @MX_file"
        }
        update.message.reply_text(credits_text.get(lang, credits_text["en"]))
        return

    # جستجوی مقاله ویکی‌پدیا
    wiki = wikipediaapi.Wikipedia(lang)
    page = wiki.page(text)

    if page.exists():
        update.message.reply_text(page.summary[:4000])
    else:
        update.message.reply_text("No article found.")

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    dp = Dispatcher(bot, None, workers=0)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.process_update(update)
    return "ok"

@app.route("/")
def index():
    return "Millow Wiki Bot is running."
