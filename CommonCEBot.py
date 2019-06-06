import json
import os
import random

from telegram import Bot, Sticker
from telegram.error import BadRequest, RetryAfter, TimedOut, NetworkError
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

config = {}
database = {}
userState = {}
randomStickerKeyword = '#&#&#random#$#$#'
randomStickerCount = 0
rand = random.SystemRandom()

def loadConfig():
    global config
    
    with open('config.json') as f:
        config = json.load(f)

def loadDatabase():
    global database
    
    if os.path.exists('database.json'):
        with open('database.json') as f:
            database = json.load(f)
    else:
        database = {}

def saveDatabase():
    global database

    with open('database.json','w') as f:
        f.write(json.dumps(database, indent=4, sort_keys=True))

def loadUserState():
    global userState
    
    if os.path.exists('userState.json'):
        with open('userState.json') as f:
            userState = json.load(f)
    else:
        userState = {}

def saveUserState():
    global userState

    with open('userState.json','w') as f:
        f.write(json.dumps(userState, indent=4, sort_keys=True))

def addKeyword(userId, keyword):
    global userState

    userState[userId] = keyword
    saveUserState()

def addSticker(userId, sticker):
    global userState, database

    if isinstace(sticker, Sticker):
        fileId = sticker.file_id
    elif isinstace(sticker, str):
        fileId = sticker
    else:
        return

    if userId in userState:
        keyword = userState[userId]
        if keyword in database:
            database[keyword].add(fileId)
        else:
            database[keyword] = set().add(fileId)
        del userState[userId]

        saveDatabase()
        saveUserState()
    else:
        return

def sendSticker(text):
    if database:
        for keyword, fileIds in database:
            if keyword in text:
                randNumber = rand.randint(0,len(fileIds)-1)
                return fileIds[randNumber]
            else:
                pass

        randomStickerCount =- 1
        if randomStickerCount == 0:
            randomStickerCount = rand.randint(1, 99)
            if randomStickerKeyword in database:
                fileIds = database[randomStickerKeyword]
                randNumber = rand.randint(0,len(fileIds)-1)
                return fileIds[randNumber]
            else:
                return None
        else:
            return None
    else:
        return None

def main():
    global config, randomStickerCount

    loadConfig()
    loadDatabase()
    loadUserState()
    randomStickerCount = rand.randint(1, 99)
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

    @command(CommandHandler, 'start', filters=Filters.private)
    def start_bot(bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text='迷迭迷迭帕里桑', reply_to_message_id=update.message.message_id)

    @command(CommandHandler, 'add', filters=Filters.private, pass_args=True)
    def add_bot(bot, update, args):
        if str(update.message.from_user.id) == config['owner_id']:
            addKeyword(update.message.from_user.id, args[0])
            bot.sendMessage(chat_id=update.message.chat_id, text='please send the sticker.', reply_to_message_id=update.message.message_id)
        else:
            bot.sendMessage(chat_id=update.message.chat_id, text='401', reply_to_message_id=update.message.message_id)

    @command(CommandHandler, 'addRandom', filters=Filters.private)
    def addRandom_bot(bot, update):
        if str(update.message.from_user.id) == config['owner_id']:
            addKeyword(update.message.from_user.id, randomStickerKeyword)
            bot.sendMessage(chat_id=update.message.chat_id, text='please send the sticker.', reply_to_message_id=update.message.message_id)
        else:
            bot.sendMessage(chat_id=update.message.chat_id, text='401', reply_to_message_id=update.message.message_id)

    @command(MessageHandler, Filters.private & Filters.sticker)
    def sticker_bot(bot, update):
        if str(update.message.from_user.id) == config['owner_id']:
            addSticker(update.message.from_user.id, update.message.sticker)
            bot.sendMessage(chat_id=update.message.chat_id, text='done.', reply_to_message_id=update.message.message_id)
        else:
            bot.sendMessage(chat_id=update.message.chat_id, text='401', reply_to_message_id=update.message.message_id)
    
    @command(MessageHandler, Filters.text & (~ Filters.private))
    def chat_bot(bot, update):
        fileId = sendSticker(update.message.text)
        if fileId:
            bot.sendSticker(chat_id=update.message.chat_id, sticker=fileId)

    @command(CommandHandler, 'exit', filters=Filters.private)
    def exit_bot(bot, update):
        if str(update.message.from_user.id) == config['owner_id']:
            bot.sendMessage(chat_id=update.message.chat_id, text='done', reply_to_message_id=update.message.message_id)
            os._exit(0)
        else:
            bot.sendMessage(chat_id=update.message.chat_id, text='401', reply_to_message_id=update.message.message_id)

    updater.start_polling()

if __name__ == '__main__':
    main()