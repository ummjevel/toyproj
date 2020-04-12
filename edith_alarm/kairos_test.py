# 두 번 정도 선택할 수 있는 핸들러 생성해서 실행해보기
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, ConversationHandler, CallbackQueryHandler

list_message_ko = [
    "미팅 알림을 생성하시겠어요?" # first create
    ,"생성을 취소합니다."
    ,"알림을 반복하시겠어요?"   # second repeat
    ,"{} 요일을 선택해주세요"      # third choose
    ,"멤버들과 알림 시간을 언제 정하시겠어요?"  #fourth ask # fifth vote
    ,"알림 시간을 투표하겠습니다. 방에 계신 분들은 투표를 위해 /h [시간]을 입력해주세요. 알림 시간이 이미 확정된 경우 /f [시간] 을 입력하시면 해당 시간으로 투표는 종료됩니다."
    ,"알림 시간을 정할 알림을 당일 드리겠습니다. 몇 시부터 멤버들과 정하시겠어요?" # 시간 버튼.. # sixth ensure
    ,"수고하셨습니다. {}시로 알림시간이 확정되었습니다." # seventh fix
    ,"미리알림을 설정하시겠어요?" # eighth preacq
    ,"설정이 완료되었습니다." # ninth comp"
    ,"알겠습니다. 멤버들과 시간을 정할 수 있도록 당일 {}시에 알림을 드릴게요."
    ,"네. 반복하지 않겠습니다."
    ,"네. 알림은 반복됩니다."
]
list_button_ko = [
    ["예", "yes"]
    ,["아니오", "no"]
    ,["이전", "prev"]
    ,["취소", "cancel"]
    ,["지금부터", "now"]
    ,["당일", "tday"]
]

list_command = [
    "create"
    ,"h"
    ,"f"
    ,"delete"
    ,"show"
]

CREATE, REPEAT, CHOOSE, ASK, VOTE, ENSURE, FIX, PREACQ, COMP = range(9)

# 언어 설정
list_button = list_button_ko
list_message = list_message_ko

def makebutton(index):
    return [InlineKeyboardButton(list_button[index][0], callback_data=list_button[index][1])]

kairos_token = "1110549427:AAHYDs1Lo3zUmSUpprI_qN04m-ekRSfvhxw"
updater = Updater(kairos_token) #, use_context=True)

def hello(update, context):
    context.message.reply_text("got message!")

def create(update, context):
    reply_markup = InlineKeyboardMarkup([makebutton(0), makebutton(1)])
    context.message.reply_text(list_message[0], reply_markup=reply_markup)
    #context.message.reply_text("got message!")
    return REPEAT
    #return ConversationHandler.END

def repeat(update, context):
    query = context.callback_query
    if query.data == "no":
        update.edit_message_text(
            chat_id=query.message.chat_id
            ,message_id=query.message.message_id
            ,text=list_message[1] # 생성 취소
        )
        return ConversationHandler.END

    update.edit_message_text(
        chat_id=query.message.chat_id
        ,message_id=query.message.message_id
        ,text=list_message[2] # 반복할거야?
    )
    reply_markup = InlineKeyboardMarkup([makebutton(0), makebutton(1)]) #, makebutton(2)]) # 예 아니오 이전
    update.edit_message_reply_markup(
        chat_id=query.message.chat_id
        ,message_id=query.message.message_id
        ,reply_markup=reply_markup
    )
    return CHOOSE

def choose(update, context):
    query = context.callback_query
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
        chat_id=query.message.chat_id
        ,message_id=query.message.message_id
        ,text=list_message[3].format(choose_msg) # 요일선택
    )
    reply_markup = InlineKeyboardMarkup([makebutton(0), makebutton(1)]) #, makebutton(2)]) # 일월화수목금토
    update.edit_message_reply_markup(
        chat_id=query.message.chat_id
        ,message_id=query.message.message_id
        ,reply_markup=reply_markup
    )
    return ASK

def ask(update, context):
    query = context.callback_query
    update.edit_message_text(
        chat_id=query.message.chat_id
        ,message_id=query.message.message_id
        ,text=list_message[4] # 시간 언제정할겨
    )
    reply_markup = InlineKeyboardMarkup([makebutton(4), makebutton(5), makebutton(2)]) # 지금 당일 이전
    update.edit_message_reply_markup(
        chat_id=query.message.chat_id
        ,message_id=query.message.message_id
        ,reply_markup=reply_markup
    )
    return VOTE
    #return ConversationHandler.END

def vote(update, context):
    query = context.callback_query

    if query.data == "now":
        update.edit_message_text(
            chat_id=query.message.chat_id
            ,message_id=query.message.message_id
            ,text=list_message[5] # 투표하라
        )
        return ConversationHandler.END

    elif query.data == "tday":
        update.edit_message_text(
            chat_id=query.message.chat_id
            ,message_id=query.message.message_id
            ,text=list_message[6] # 당일 알림 언제할래
        )
        reply_markup = InlineKeyboardMarkup([makebutton(0), makebutton(1), makebutton(2)])
        update.edit_message_reply_markup(
            chat_id=query.message.chat_id
            ,message_id=query.message.message_id
            ,reply_markup=reply_markup
        )
        return ENSURE
        #return ConversationHandler.END
    # elif query.data == "prev":
    #     return ASK

def ensure(update, context):
    query = context.callback_query
    update.edit_message_text(
        chat_id=query.message.chat_id
        ,message_id=query.message.message_id
        ,text=list_message[10] # 시간 설정 완료했으니 당일 알림 줄게
    )
    return ConversationHandler.END

# def fix(update, context):
#     query = context.callback_query
#     update.edit_message_text(
#         chat_id=query.message.chat_id
#         ,message_id=query.message.message_id
#         ,text=list_message[7] # 수고했으 시간정하기 완료
#     )
#     reply_markup = InlineKeyboardMarkup([makebutton(0), makebutton(1), makebutton(2)])
#     update.edit_message_reply_markup(
#         chat_id=query.message.chat_id
#         ,message_id=query.message.message_id
#         ,reply_markup=reply_markup
#     )
#     return PREACQ

# def preacq(update, context):
#     query = context.callback_query
#     update.edit_message_text(
#         chat_id=query.message.chat_id
#         ,message_id=query.message.message_id
#         ,text=list_message[8] # 미리알림할래
#     )
#     reply_markup = InlineKeyboardMarkup([makebutton(0), makebutton(1), makebutton(2)])
#     update.edit_message_reply_markup(
#         chat_id=query.message.chat_id
#         ,message_id=query.message.message_id
#         ,reply_markup=reply_markup
#     )
#     return COMP

# def comp(update, context):
#     query = context.callback_query
#     update.edit_message_text(
#         chat_id=query.message.chat_id
#         ,message_id=query.message.message_id
#         ,text=list_message[9] # 설정완료
#     )
#     # reply_markup = InlineKeyboardMarkup([makebutton(0), makebutton(1), makebutton(2)])
#     # update.edit_message_reply_markup(
#     #     chat_id=query.message.chat_id
#     #     ,message_id=query.message.message_id
#     #     ,reply_markup=reply_markup
#     # )
#     return ConversationHandler.END

conv_handler = ConversationHandler(
    entry_points=[CommandHandler(list_command[0], create)]
    ,states={
         CREATE: [CallbackQueryHandler(create)]
        ,REPEAT: [CallbackQueryHandler(repeat)]
        ,CHOOSE: [CallbackQueryHandler(choose)]
        ,ASK: [CallbackQueryHandler(ask)]
        ,VOTE: [CallbackQueryHandler(vote)]
        ,ENSURE: [CallbackQueryHandler(ensure)]
        # ,FIX: [CallbackQueryHandler(fix)]
        # ,PREACQ: [CallbackQueryHandler(preacq)]
        # ,COMP: [CallbackQueryHandler(comp)]
    }
    ,fallbacks=[CommandHandler(list_command[0], create)]
)

updater.dispatcher.add_handler(conv_handler)

#updater.dispatcher.add_handler(CommandHandler('create', create))
print("start")
updater.start_polling()
updater.idle()
