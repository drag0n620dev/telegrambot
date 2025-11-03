from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CallbackQueryHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import holidays
import logging
import os

# === Einstellungen ===
BOT_TOKEN = os.getenv("BOT_TOKEN", "DEIN_DEFAULT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID", "123456789"))
Timezone= os.getenv("TIMEZONE", "Europe/Berlin")
Bundesland = os.getenv("BUNDESLAND", "RP")
Hour = int(os.getenv("HOUR", "5"))
Minute = int(os.getenv("MINUTE", "20"))
Debugging = os.getenv("DEBUGGING", "False")

# Logging aktivieren
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Scheduler als Hintergrundprozess
scheduler = BackgroundScheduler(timezone=Timezone)

# === Globale Status-Variable ===
# True = Nachricht senden, False = nicht senden
user_state = {"receive_message": True}

# === Funktion zum Senden der Nachricht ===
def send_message():
    
    MESSAGE_TEXT = "Guten Morgen! 🌞 Bitte vergesse deinen Arbeitschip nicht."

    # Benutzer will keine Nachricht → abbrechen
    if not user_state.get("receive_message", True):
        logging.info("Benutzer hat Nachrichten deaktiviert – überspringe Versand.")
        user_state["receive_message"] = True
        return
    
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    
    # Samstag oder Sonntag überspringen
    if today.weekday() >= 5:
        logging.info("Wochenende – keine Nachricht gesendet.")
        return
    
    heute = today.year
    morgen = tomorrow.year

    # Feiertage Rheinland-Pfalz
    de_holidays          = holidays.Germany(years=heute,  prov=Bundesland)
    de_holidays_tomorrow = holidays.Germany(years=morgen, prov=Bundesland)

    # Feiertag prüfen
    if today in de_holidays:
        logging.info(f"Heute ({today}) ist Feiertag: {de_holidays[today]}")
        return
 
    # === Optional: Buttons ===
    buttons = [
        [InlineKeyboardButton("👍 Ja", callback_data="yes")],
        [InlineKeyboardButton("❌ Nein", callback_data="no")]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    # Prüfen, ob morgen Wochenende oder Feiertag ist
    tomorrow_is_weekend = tomorrow.weekday() >= 5  # 5=Samstag, 6=Sonntag
    tomorrow_is_holiday = tomorrow in de_holidays_tomorrow

    # === Nachricht anpassen ===
    bot = Bot(token=BOT_TOKEN)
    if tomorrow_is_weekend or tomorrow_is_holiday:
        if tomorrow_is_weekend:
            reason = "Wochenende 💤"
        else:
            reason = f"Feiertag ({de_holidays[tomorrow]}) 🎉"
        MESSAGE_TEXT += f"\nMorgen ist {reason}, also bekommst du **morgen keine Nachricht.**"
        bot.send_message(
            chat_id=CHAT_ID,
            text=MESSAGE_TEXT
        )
    else:
        MESSAGE_TEXT += "\nBist du morgen im Büro in Ludwigshafen?"
        bot.send_message(
            chat_id=CHAT_ID,
            text=MESSAGE_TEXT,
            reply_markup=keyboard
        )
    logging.info(f"Nachricht gesendet am {today} um {datetime.datetime.now().time()}")

# === Callback-Funktion bei Button-Klicks ===
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "yes":
        user_state["receive_message"] = True
        reply_text = "Sehr gut, dann bis morgen zu deiner täglichen Nachricht! 😊"
    elif query.data == "no":
        user_state["receive_message"] = False
        reply_text = "Dann wirst du mich morgen leider nicht hören – hab trotzdem einen schönen Tag! 🌤️"
    else:
        reply_text = "🤖 Ich weiß nicht, was du meinst 😅"

    query.edit_message_text(
        text=f"{query.message.text}\n\n➡️ {reply_text}"
    )

# === Bot starten ===
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Handler registrieren
    dp.add_handler(CallbackQueryHandler(button_handler))

    
    if Debugging == "True":
        # Test
        scheduler.add_job(send_message, "interval", seconds=Minute)
    else:
        # Scheduler starten (täglich um 4:40 Uhr)
        scheduler.add_job(send_message, "cron", hour=Hour, minute=Minute)

    scheduler.start()

    logging.info("Bot gestartet. Warte auf geplante Aufgaben und Benutzeraktionen...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
