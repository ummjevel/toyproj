# edith_alarm

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackQueryHandler, ConversationHandler, JobQueue
#from datetime import datetime, date, time, timezone

from telegrambot import TelBot


#SUN, MON, TUE, WED, THU, FRI, SAT = range(7)
dict_week = {"Sunday":0, "Monday":1, "Tuesday":2, "Wednesday":3, "Thursday":4, "Friday":5, "Saturday":6}
list_selected_week = [False, False, False, False, False, False, False]

# this needs refactoring using loop..
btnlist_yn = [
     [InlineKeyboardButton(text="Yes", callback_data="yes")]
    ,[InlineKeyboardButton(text="No", callback_data="no")]
    ]
btnmark_yn = InlineKeyboardMarkup(btnlist_yn)

btnlist_week = [
     [InlineKeyboardButton(text="Sunday", callback_data="Sunday")]
    ,[InlineKeyboardButton(text="Monday", callback_data="Monday")]
    ,[InlineKeyboardButton(text="Tuesday", callback_data="Tuesday")]
    ,[InlineKeyboardButton(text="Wednesday", callback_data="Wednesday")]
    ,[InlineKeyboardButton(text="Thursday", callback_data="Thursday")]
    ,[InlineKeyboardButton(text="Friday", callback_data="Friday")]
    ,[InlineKeyboardButton(text="Saturday", callback_data="Saturday")]
    ,[InlineKeyboardButton(text="Ok. I've made my choice.'", callback_data="com")]
]

btnmark_week = InlineKeyboardMarkup(btnlist_week)

btnlist_nl = [
     [InlineKeyboardButton(text="now", callback_data="now")]
    ,[InlineKeyboardButton(text="later", callback_data="day")]
    ]
btnmark_nl = InlineKeyboardMarkup(btnlist_nl)

btnlist_hour = [
     [InlineKeyboardButton(text="9", callback_data="9")]
    ,[InlineKeyboardButton(text="12", callback_data="12")]
    ,[InlineKeyboardButton(text="15", callback_data="15")]
    ,[InlineKeyboardButton(text="17", callback_data="17")]
    ]
btnmark_hour = InlineKeyboardMarkup(btnlist_hour)

btnlist_remin = [
     [InlineKeyboardButton(text="3 hour ago", callback_data="3")]
    ,[InlineKeyboardButton(text="1 hour ago", callback_data="1")]
    ,[InlineKeyboardButton(text="30 min ago", callback_data="30")]
    ,[InlineKeyboardButton(text="10 min ago", callback_data="10")]
    ]
btnmark_remin = InlineKeyboardMarkup(btnlist_remin)

CREATE, REPEAT, ASKDAY, FIXDAY, PREACQ, CLOSE, CANCLE, COMP, CHECK = range(9)


# support annotations replace -> 3.8.2 

def hello(update, context):
        print("in hello")
        update.message.reply_text("hello!!")
        update.sendMessage(chat_id=update.message.chat_id, text="hello :0")
        print("after chatid hello")

def help(update, context):
    print("help")
    update.message.reply_text("help..")

def show(update, context):
    print("show")
    update.message.reply_text("show schedule..")

def delete(update, context):
    print("delete")
    update.message.reply_text("delete schedule..")

def create(update, context):
    print("in create")
    update.message.reply_text("Do you want create meeting alarm schedule?", reply_markup=btnmark_yn)
    return CREATE

def create_callback(update, context):
    print("in create_callback")
    # doesn't work update.message.reply_text("call create_callback")
    query = update.callback_query
    if query.data == 'yes':
        # update.edit_message_text(text="you choosed {}. does meeting schedule repeated?".format(query.data)
        #                     , chat_id=query.message.chat_id
        #                     , message_id=query.message.message_id
        #                     , reply_markup=btnmark_yn)
        print("end")
        context.bot.send_message(
            chat_id=update.message.chat_id
            , text='작업을 선택해주세요.'
            , reply_markup=btnmark_yn
        )
        #update.message.reply_text(query.data)
        #update.message.reply_text("abcabc")
        #editMessageReplyMarkup()
        return REPEAT
    else:
        return CANCLE

def repeated_callback(update, context):
    print("in repeated_callback")
    query = update.callback_query
    info_msg = ""
    if query.data == 'yes':
        info_msg = "The schedule will be repeated."
    else:
        info_msg = "The schedule will not be repeated."

    update.edit_message_text(text="you choosed '{}'. {}. Select the day of the week."
                                    .format(query.data, info_msg)
                            , chat_id=query.message.chat_id
                            , message_id=query.message.message_id
                            , reply_markup=btnmark_week)

    return CHECK

def repeated_callback_check(update, context):
    print("in repeated callback_check")
    query = update.callback_query

    if query.data == "com":
        return ASKDAY
    else:
        if list_selected_week[dict_week[query.data]] == False:
            btnlist_week[dict_week[query.data]][0].text = "✔ " + query.data
            list_selected_week[dict_week[query.data]] = True
        else:
            btnlist_week[dict_week[query.data]][0].text = query.data
            list_selected_week[dict_week[query.data]] = False
            update.edit_message_text(text="Select the day of the week."
                                , chat_id=query.message.chat_id
                                , message_id=query.message.message_id
                                , reply_markup=btnmark_week)
        return CHECK

def askday_callback(update, context):
    query = update.callback_query
    
    update.edit_message_text(text="Would you like to set the time now?"
                            , chat_id=query.message.chat_id
                            , message_id=query.message.message_id
                            , reply_markup=btnmark_nl)

    return FIXDAY

def fixday_callback(update, context):
    print("fixday_callback")
    query = update.callback_query
    if query.data == 'now':
        update.edit_message_text(text="All members enter '/[number]' to complete the setup." +
                                "Enter '/f [number]' if you want to set it up immediately without receiving all of the members' input." +
                                "You can set the notification in advance after input is completed."
                                , chat_id=query.message.chat_id
                                , message_id=query.message.message_id)
        #set Alarmbot.able_voting = True
        return CLOSE
    elif query.data == 'day':
        update.edit_message_text(text="I'll give you a notification on the same day so you can set it up. "
                                        + "Choose the time you want to be notified of the time you want to set."
                                , chat_id=query.message.chat_id
                                , message_id=query.message.message_id
                                , reply_markup=btnmark_hour)
        return PREACQ

def preacq_callback(update, context):
    print("preacq_callback")
    query = update.callback_query
    
    update.edit_message_text(text="Do you want to set up a reminder?"
                            , chat_id=query.message.chat_id
                            , message_id=query.message.message_id
                            , reply_markup=btnmark_remin)

    return COMP

def comp_callback(update, context):
    print("comp_callback")
    query = update.callback_query

    update.edit_message_text(text="Setup Completed."
                            , chat_id=query.message.chat_id
                            , message_id=query.message.message_id)

    return ConversationHandler.END

def canc_callback(update, context):
    print("canc_callback")
    query = update.callback_query

    update.edit_message_text(text="Canceled."
                            , chat_id=query.message.chat_id
                            , message_id=query.message.message_id)

    return ConversationHandler.END

def close_callback(update, context):
    print("close_callback")
    # query = update.callback_query

    print("listening voting...")

    return ConversationHandler.END

def callback_alarm(context):
    context.bot.sendMessage(chat_id=context.job.context,
                            text='BEEEEEEEEEEP!!!!')

def callback_timer(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                            text='Setting a timer for 10 seconds!')
    context.job_queue.run_once(callback_alarm, 10, context=update.message.chat_id)

def vote_alarm(update, context):
    #text_arg = context.args[0]

    context.bot.send_message(chat_id=update.message.chat_id
                            ,text='')

def vote_alarm_callback(update, context):
    context.bot.send_message(chat_id=update.message.chat_id
                            ,text='abcde')

if __name__ == "__main__":
    kairos_bot_token = "1110549427:AAHYDs1Lo3zUmSUpprI_qN04m-ekRSfvhxw"
    
    alm = TelBot("kairos", kairos_bot_token)

    dict_process = { CREATE: [CallbackQueryHandler(create_callback)]
                        , REPEAT: [CallbackQueryHandler(repeated_callback)]
                        , ASKDAY: [CallbackQueryHandler(askday_callback)]
                        , FIXDAY: [CallbackQueryHandler(fixday_callback)]
                        , PREACQ: [CallbackQueryHandler(preacq_callback)]
                        , CLOSE: [CallbackQueryHandler(close_callback)]
                        , CANCLE: [CallbackQueryHandler(canc_callback)]
                        , COMP: [CallbackQueryHandler(comp_callback)] 
                        , CHECK: [CallbackQueryHandler(repeated_callback_check)]
                    }
                        
    #alm.addHandler('c', 'create', create, dict_process, False)
    conv_handler = ConversationHandler(entry_points=[CommandHandler('create', create)]
                                , states=dict_process
                                , fallbacks=[CommandHandler('create', create)]
                                )
    alm.updater.dispatcher.add_handler(conv_handler)

    # alm.updater.dispatcher.add_handler(CommandHandler('create', create))
    # alm.updater.dispatcher.add_handler(CallbackQueryHandler(create_callback, pattern='create_yes'))
    # alm.updater.dispatcher.add_handler(CallbackQueryHandler(repeated_callback, pattern='repeat_yes'))

    #alm.updater.dispatcher.add_handler(CommandHandler('once', job_callback, pass_job_queue=True))
    
    timer_handler = CommandHandler('timer', callback_timer, pass_job_queue=True, pass_args=True)
    alm.updater.dispatcher.add_handler(timer_handler)

    alm.addHandler('c', 'f', vote_alarm, vote_alarm_callback, True)

    alm.addHandler('c', 'hello', hello, None, True)
    alm.addHandler('c', 'stop', alm.stop, None, True)

    alm.start()
