import json

from telegram import Bot
from telegram.error import BadRequest, RetryAfter, TimedOut, NetworkError
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

config = {}

def loadConfig():
    global config
    
    with open('config.json') as f:
        config = json.load(f)

def main():
    global config

    loadConfig()
    bot = Bot(config['token'])
    updater = Updater(token=config['token'])
    dispatcher = updater.dispatcher

    def command(handler, cmd=None, **kw):
        def decorater(func):
            def wrapper(*args,**kw):
                return func(*args,**kw)
            if cmd==None:
                func_hander=handler(func,**kw)
            else:
                func_hander=handler(cmd,func,**kw)
            dispatcher.add_handler(func_hander)
            return wrapper
        return decorater

    @command(CommandHandler, 'start')
    def start_bot(bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text='迷迭迷迭帕里桑', reply_to_message_id=update.message.message_id)

    updater.start_polling()

if __name__ == '__main__':
    main()