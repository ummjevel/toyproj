# basic function

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackQueryHandler, ConversationHandler

class TelBot:
    def __init__(self, name, token):
        self.bot = Bot(token=token)
        self.name = name
        self.updater = Updater(token=token, use_context=True)
        self.job = self.updater.job_queue
        self.printBot("completed parent class init.")
        print("completed init.")

    def printBot(self, context):
        '''
        printed 
        '''
        # self.bot.get_updates()[-1].message.chat_id
        current_chat_id = 99899723    # self.updater.bot.get_chat_members_count
        self.bot.sendMessage(chat_id=current_chat_id, text=context)
        print(context)

    def addHandler(self, handler_type, cmd, func, callback_func, is_pass_args):
        '''
        handler_type: 'c' - commandhandler
                      'm' - messagehandler
        cmd: handler commnand ex) create
        func: callback function name
        '''

        if handler_type == 'c':
            if callback_func is not None:
                if callback_func is not dict:
                    self.updater.dispatcher.add_handler(CommandHandler(cmd, func))
                    self.updater.dispatcher.add_handler(CallbackQueryHandler(callback_func))
                else:
                    conv_handler = ConversationHandler(entry_points=[CommandHandler(cmd, func)]
                                    , states=callback_func
                                    , fallbacks=[CommandHandler(cmd, func)]
                                    )
                    self.updater.dispatcher.add_handler(conv_handler)
            else:
                self.updater.dispatcher.add_handler(CommandHandler(cmd, func))
            
               
                
        elif handler_type == 'm':
            self.updater.dispatcher.add_handler(MessageHandler(Filters.text, func))

        print("complete add handler.")
        
    def start(self):
        self.updater.start_polling()
        self.printBot("start pooling...")
        self.updater.idle()
        print("start polling...")

    def stop(self, update, context):
        print("start stop.")
        context.message.reply_text("got text bot will stop..")
        update.sendMessage(chat_id=99899723, text="will stop :0")
        # update.bot.sendMessage(chat_id=99899723, text="will stop :0")
        print("after print stop")
        context.updater.stop()
        print("stop.")


        
class KairosBot(TelBot, object):

    def __init__(self, name, token):
        super(KairosBot, self).__init__(name, token)
        super(KairosBot, self).printBot("completed init.")
        # self.is_repeat = False
        # self.repeat_week = [False, False, False, False, False, False, False]
        # self.alarm_datetime = []    # list, item type is datetime
        # self.preacquaintance = datetime.now()
        # self.able_voting = False
        # self.voting = [0] * 24

        #self.CREATE, self.REPEAT, self.ASKDAY, self.FIXDAY, self.PREACQ, self.CLOSE, self.CANCLE, self.COMP, self.CHECK = range(9)

    

