# 두 번 정도 선택할 수 있는 핸들러 생성해서 실행해보기
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, ConversationHandler, CallbackQueryHandler
import json

list_message_ko = [
    "미팅 알림을 생성하시겠어요?" # first create
    ,"생성을 취소합니다."
    ,"알림을 반복하시겠어요?"   # second repeat
    ,"{} 요일을 선택해주세요"      # third choose
    ,"멤버들과 알림 시간을 언제 정하시겠어요?"  #fourth ask # fifth vote
    ,"알림 시간을 투표하겠습니다. 방에 계신 분들은 투표를 위해 /v [시간]을 입력해주세요. 알림 시간이 이미 확정된 경우 /f [시간] 을 입력하시면 해당 시간으로 투표는 종료됩니다."
    ,"알림 시간을 정할 알림을 당일 드리겠습니다. 몇 시부터 멤버들과 정하실지 /t [0-23] 형태로 입력해주세요. " # 시간 버튼.. # sixth ensure
    ,"수고하셨습니다. {}시로 알림시간이 확정되었습니다. " # seventh fix
    ,"미리알림을 설정하시겠어요?" # eighth preacq
    ,"설정이 완료되었습니다." # ninth comp"
    ,"알겠습니다. 멤버들과 시간을 정할 수 있도록 당일 {}시에 알림을 드릴게요. "
    ,"네. 반복하지 않겠습니다."
    ,"네. 알림은 반복됩니다."
    ,"요일을 선택해주세요. 완료 시 선택완료 버튼을 눌러주세요."
    ,"올바른 형태로 입력해주세요. /{} 다음에는 0부터 23 사이의 숫자가 들어가야 합니다."
    ,"미리알림을 받을 시간을 선택해주세요." # 15
    ,"지금 투표하고 싶으실 경우 아래 버튼을 눌러주세요." # 16
    ,"{} 시로 저장되었고, {} 명의 투표가 남았습니다." # 17
    ,"현재 상태: \n" # 18
    ,"    {}시: {}명\n" # 19
]
list_button_ko = [
    ["예", "yes"]
    ,["아니오", "no"]
    ,["이전", "prev"]
    ,["취소", "cancel"]
    ,["지금부터", "now"]
    ,["당일", "tday"]
    ,["일요일", "Sunday"] # 6
    ,["월요일", "Monday"] # 7
    ,["화요일", "Tuesday"] # 8
    ,["수요일", "Wednesday"] # 9
    ,["목요일", "Thursday"] # 10
    ,["금요일", "Friday"] # 11
    ,["토요일", "Saturday"] # 12
    ,["선택완료", "ok"] # 13
    ,["3시간 전", "b3"] # 14
    ,["1시간 전", "b1"] # 15
    ,["30분 전", "b30"] # 16
    ,["10분 전", "b10"] # 17
    ,["설정안함", "cancel"] # 18
]

list_week = [
     "Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"
]
list_week_selected = [False, False, False, False, False, False, False]

list_command = [
    "create"
    ,"h"
    ,"f"
    ,"delete"
    ,"show"
]

dict_data = {}

CREATE, REPEAT, CHOOSE, CHOOSE_CHK, ASK, VOTE, ENSURE, FIX, PREACQ, COMP, FIX_TDAY, PREACQ2, ASK_CHK = range(13)

# 언어 설정
list_button = list_button_ko
list_message = list_message_ko

# { 채널 id: 현재상태... } list_channel.update(a=1)
list_channel = {}
list_reserv = [] # json format { chat_id:[{repeat:True, week:[], preacq:11,}] }


def makebutton(index):
    return [InlineKeyboardButton(list_button[index][0], callback_data=list_button[index][1])]

kairos_token = "1110549427:AAHYDs1Lo3zUmSUpprI_qN04m-ekRSfvhxw"
updater = Updater(kairos_token) #, use_context=True)

def hello(update, context):
    context.message.reply_text("got message!")

def create(update, context):
    reply_markup = InlineKeyboardMarkup([makebutton(0), makebutton(1)])
    context.message.reply_text(list_message[0], reply_markup=reply_markup)
    chat_id = context.message.chat_id
    list_channel[chat_id] = 'create'

    dict_data[chat_id] = {'repeat': 'n', 'week':['sun','tue'], 'state':'create'}
    dict_data[chat_id]['week'].append('wed')
    #dict_data[chat_id]['week'].remove('sun')
    #context.message.reply_text("got message!")
    return REPEAT
    #return ConversationHandler.END

def repeat(update, context):
    query = context.callback_query
    chat_id = query.message.chat_id
    list_channel[chat_id] = 'repeat'
    if query.data == "no":
        update.edit_message_text(
            chat_id=chat_id
            ,message_id=query.message.message_id
            ,text=list_message[1] # 생성 취소
        )
        return ConversationHandler.END

    update.edit_message_text(
        chat_id=chat_id
        ,message_id=query.message.message_id
        ,text=list_message[2] # 반복할거야?
    )
    reply_markup = InlineKeyboardMarkup([makebutton(0), makebutton(1)]) # 예 아니오 이전
    update.edit_message_reply_markup(
        chat_id=chat_id
        ,message_id=query.message.message_id
        ,reply_markup=reply_markup
    )
    return CHOOSE

def choose(update, context):
    query = context.callback_query
    chat_id = query.message.chat_id
    list_channel[chat_id] = 'choose'
    choose_msg = ""
    if query.data == "yes":
        choose_msg = list_message[12]
    elif query.data == "no":
        choose_msg = list_message[11]
    # 실수는 용납하지 않는다.
    # else:
    #     reply_markup = InlineKeyboardMarkup([makebutton(0), makebutton(1)])
    #     context.message.reply_text(list_message[0], reply_markup=reply_markup)
    #     return CREATE

    update.edit_message_text(
        chat_id=chat_id
        ,message_id=query.message.message_id
        ,text=list_message[3].format(choose_msg) # 요일선택
    )
    reply_markup = InlineKeyboardMarkup([makebutton(6), makebutton(7),makebutton(8), makebutton(9),makebutton(10), makebutton(11),makebutton(12),makebutton(13)]) #, makebutton(2)]) 
    update.edit_message_reply_markup(
        chat_id=chat_id
        ,message_id=query.message.message_id
        ,reply_markup=reply_markup
    )
    return CHOOSE_CHK

def choose_chk(update, context):
    query = context.callback_query
    chat_id = query.message.chat_id
    list_channel[chat_id] = 'choose_chk'

    if query.data == "ok":
        # save week
        # 
        update.edit_message_text(
            chat_id=chat_id
            ,message_id=query.message.message_id
            ,text=list_message[4] # 시간 언제정할겨
        )
        reply_markup = InlineKeyboardMarkup([makebutton(4), makebutton(5)]) #, makebutton(2)]) # 지금 당일 이전
        update.edit_message_reply_markup(
            chat_id=chat_id
            ,message_id=query.message.message_id
            ,reply_markup=reply_markup
        )
        return ASK
    else:
        
        week_index = list_week.index(query.data)
        if list_week_selected[week_index] == False:
            list_button[week_index + 6][0] = "✔ " + list_button[week_index + 6][0]
            list_week_selected[week_index] = True
            reply_markup = InlineKeyboardMarkup([makebutton(6), makebutton(7),makebutton(8), makebutton(9),makebutton(10), makebutton(11),makebutton(12),makebutton(13)]) # 일월화수목금토확인
            update.edit_message_text(text=list_message[13]
                                , chat_id=chat_id
                                , message_id=query.message.message_id
                                , reply_markup=reply_markup)
        else:
            list_button[week_index + 6][0] = list_button[week_index + 6][0][2:]
            list_week_selected[week_index] = False
            reply_markup = InlineKeyboardMarkup([makebutton(6), makebutton(7),makebutton(8), makebutton(9),makebutton(10), makebutton(11),makebutton(12),makebutton(13)]) # 일월화수목금토확인
            update.edit_message_text(text=list_message[13]
                                , chat_id=chat_id
                                , message_id=query.message.message_id
                                , reply_markup=reply_markup)
    return CHOOSE_CHK


def ask(update, context):
    query = context.callback_query
    chat_id = query.message.chat_id
    list_channel[chat_id] = 'ask'
    if query.data == "now":
        update.edit_message_text(
            chat_id=chat_id
            ,message_id=query.message.message_id
            ,text=list_message[5] # 투표하라
        )
        return ConversationHandler.END

    elif query.data == "tday":
        update.edit_message_text(
            chat_id=chat_id
            ,message_id=query.message.message_id
            ,text=list_message[6] + list_message[16] # 당일 알림 언제할래
        )
        reply_markup = InlineKeyboardMarkup([makebutton(4)]) #, makebutton(2)])
        update.edit_message_reply_markup(
            chat_id=chat_id
            ,message_id=query.message.message_id
            ,reply_markup=reply_markup
        )
        #return ENSURE
        return ASK_CHK
    # elif query.data == "prev":
    #     return ASK

    # return VOTE
    #return ConversationHandler.END

def ask_chk(update, context):
    query = context.callback_query
    chat_id = query.message.chat_id
    list_channel[chat_id] = 'ask_chk'
    if query.data == "now":
        update.edit_message_text(
            chat_id=chat_id
            ,message_id=query.message.message_id
            ,text=list_message[5] # 투표하라
        )
        
    return ConversationHandler.END

def vote(update, context):
    query = context.callback_query
    chat_id = query.message.chat_id
    list_channel[chat_id] = 'vote'
    update.edit_message_text(
            chat_id=chat_id
            ,message_id=query.message.message_id
            ,text="in vote" 
        )
    return ConversationHandler.END

def ensure(update, context):
    query = context.callback_query
    chat_id = query.message.chat_id
    # fix_chk
    list_channel[chat_id] = 'ensure'
    update.edit_message_text(
        chat_id=chat_id
        ,message_id=query.message.message_id
        ,text=list_message[10] # 시간 설정 완료했으니 당일 알림 줄게
    )
    return ConversationHandler.END

def fix(update, context):
    query = context.callback_query
    chat_id = query.message.chat_id
    list_channel[chat_id] = 'fix'
    update.edit_message_text(
        chat_id=chat_id
        ,message_id=query.message.message_id
        ,text=list_message[7] # 수고했으 시간정하기 완료
    )
    reply_markup = InlineKeyboardMarkup([makebutton(0), makebutton(1)]) #, makebutton(2)])
    update.edit_message_reply_markup(
        chat_id=chat_id
        ,message_id=query.message.message_id
        ,reply_markup=reply_markup
    )
    return PREACQ

def preacq(update, context):
    query = context.callback_query
    chat_id = query.message.chat_id
    list_channel[chat_id] = 'preacq'
    update.edit_message_text(
        chat_id=chat_id
        ,message_id=query.message.message_id
        ,text=list_message[8] # 미리알림할래
    )
    reply_markup = InlineKeyboardMarkup([makebutton(0), makebutton(1)]) #, makebutton(2)])
    update.edit_message_reply_markup(
        chat_id=chat_id
        ,message_id=query.message.message_id
        ,reply_markup=reply_markup
    )
    return PREACQ2

def preacq2(update, context):
    query = context.callback_query
    chat_id = query.message.chat_id
    list_channel[chat_id] = 'preacq2'
    if query.data == "yes":
        # 언제 미리알림 할래
        update.edit_message_text(
            chat_id=chat_id
            ,message_id=query.message.message_id
            ,text=list_message[15] # 미리알림할 시간 선택
        )
        # 3h 1h 30min 10min cancel
        reply_markup = InlineKeyboardMarkup([makebutton(14), makebutton(15),makebutton(16), makebutton(17), makebutton(18)]) 
        update.edit_message_reply_markup(
            chat_id=chat_id
            ,message_id=query.message.message_id
            ,reply_markup=reply_markup
        )
        return COMP
    elif query.data == "no":
        update.edit_message_text(
            chat_id=chat_id
            ,message_id=query.message.message_id
            ,text=list_message[9] # 설정완료
        )
        return ConversationHandler.END

def comp(update, context):
    query = context.callback_query
    chat_id = query.message.chat_id
    list_channel[chat_id] = 'comp'
    update.edit_message_text(
        chat_id=chat_id
        ,message_id=query.message.message_id
        ,text=list_message[9] # 설정완료
    )
    # reply_markup = InlineKeyboardMarkup([makebutton(0), makebutton(1), makebutton(2)])
    # update.edit_message_reply_markup(
    #     chat_id=query.message.chat_id
    #     ,message_id=query.message.message_id
    #     ,reply_markup=reply_markup
    # )
    return ConversationHandler.END

def fixtime_tday(update, context, args):
    chat_id = context.message.chat_id
    list_channel[chat_id] = 'fixtime_tday'
    #if args[0] >= 0 and args[0] <= 23 then save, or show message and go fix_chk
    input_time = int(args[0])
    if 0 <= input_time and input_time <= 23:
        # save
        reply_markup = InlineKeyboardMarkup([makebutton(0), makebutton(1)]) #, makebutton(2)])
        context.message.reply_text(list_message[10].format(args[0]) + list_message[8], reply_markup=reply_markup) 
         # 시간 설정 완료했으니 당일 알림 줄게 # 미리알림 하쉴?
        return PREACQ2
    else:
        context.message.reply_text(list_message[14].format('t')) # 제대로 입력하라고 했잖니 0-23
        return ConversationHandler.END

def forcefixtime(update, context, args):
    chat_id = context.message.chat_id
    list_channel[chat_id] = 'forcefixtime'
    #if args[0] >= 0 and args[0] <= 23 then save, or show message and go fix_chk
    input_time = int(args[0])
    if 0 <= input_time and input_time <= 23:
        # save
        # ㅅㄱ {} 시로 저장완료 미리알림 하쉴?
        reply_markup = InlineKeyboardMarkup([makebutton(0), makebutton(1)]) #, makebutton(2)])
        context.message.reply_text(list_message[7].format(args[0]) + list_message[8], reply_markup=reply_markup) 
        return PREACQ2
    else:
        context.message.reply_text(list_message[14].format('f')) # 제대로 입력하라고 했잖니 0-23
        return ConversationHandler.END

def votetime(update, context, args):
    chat_id = context.message.chat_id
    list_channel[chat_id] = 'votetime'
    input_time = int(args[0])
    if 0 <= input_time and input_time <= 23:
        totalCnt = 1
        votedCnt = 0
        # save
        if totalCnt == votedCnt:
            reply_markup = InlineKeyboardMarkup([makebutton(0), makebutton(1)]) #, makebutton(2)])
            context.message.reply_text(list_message[7].format(args[0]) + list_message[8], reply_markup=reply_markup) 
            return PREACQ2
        else:
            # {} 시로 저장되었고, {} 명의 투표가 남았습니다. 17
            # "현재 상태: \n" 18
            #  "{}시: {}명\n" 19
            # 투표를 중복으로 했을 경우, 수정되도록. 사람 id 를 같이 저장할 것.
            # 채널의 인원과 vote 된 수를 비교하여 같으면 시간 설정
            context.message.reply_text(list_message[17]) # 
            return ConversationHandler.END
    else:
        context.message.reply_text(list_message[14].format('h')) # 제대로 입력하라고 했잖니 0-23
        return ConversationHandler.END

conv_handler = ConversationHandler(
    entry_points=[CommandHandler(list_command[0], create)]
    ,states={
         CREATE: [CallbackQueryHandler(create)]
        ,REPEAT: [CallbackQueryHandler(repeat)]
        ,CHOOSE: [CallbackQueryHandler(choose)]
        ,CHOOSE_CHK: [CallbackQueryHandler(choose_chk)]
        ,ASK: [CallbackQueryHandler(ask)]
        ,ASK_CHK: [CallbackQueryHandler(ask_chk)]
        ,VOTE: [CallbackQueryHandler(vote)]
        #,ENSURE: [CallbackQueryHandler(ensure)]
        #,FIX: [CallbackQueryHandler(fix)]
        ,PREACQ: [CallbackQueryHandler(preacq)]
        ,PREACQ2: [CallbackQueryHandler(preacq2)]
        ,COMP: [CallbackQueryHandler(comp)]
        # ,FIX_TDAY: [CallbackQueryHandler(fixtime_tday)]
    }
    ,fallbacks=[CommandHandler(list_command[0], create)]
)

updater.dispatcher.add_handler(conv_handler)

conv_handler2 = ConversationHandler(
    entry_points=[CommandHandler('t', fixtime_tday, pass_args=True)]
    ,states={
        PREACQ2: [CallbackQueryHandler(preacq2)]
        ,COMP: [CallbackQueryHandler(comp)]
        # ,FIX_TDAY: [CallbackQueryHandler(fixtime_tday)]
    }
    ,fallbacks=[CommandHandler('t', fixtime_tday, pass_args=True)]
)
updater.dispatcher.add_handler(conv_handler2)

conv_handler3 = ConversationHandler(
    entry_points=[CommandHandler('f', forcefixtime, pass_args=True)]
    ,states={
        PREACQ2: [CallbackQueryHandler(preacq2)]
        ,COMP: [CallbackQueryHandler(comp)]
        # ,FIX_TDAY: [CallbackQueryHandler(fixtime_tday)]
    }
    ,fallbacks=[CommandHandler('f', forcefixtime, pass_args=True)]
)
updater.dispatcher.add_handler(conv_handler3)

#updater.dispatcher.add_handler(CommandHandler('f', forcefixtime, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('v', votetime, pass_args=True))


# updater.dispatcher.add_handler(CommandHandler('create', create))
print("start")
updater.start_polling()
updater.idle()
