from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
import telegram

TOKEN = '5201716263:AAEVOEABzrdiN_AGB369QGOVcsVwsBsCWp0'

updater = Updater(TOKEN, use_context=True)

bot = telegram.Bot(TOKEN)


def send_message(update: Update, context: CallbackContext, text):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text)

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Hi")


updater.dispatcher.add_handler(CommandHandler('start', start))


updater.start_polling()
