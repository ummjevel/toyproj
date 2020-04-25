# 두 번 정도 선택할 수 있는 핸들러 생성해서 실행해보기
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, ConversationHandler, CallbackQueryHandler
import json

from collections import Counter 

from telegram import Bot

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
    ,"투표 현황: \n" # 18
    ,"    {}시: {}명\n" # 19
    ,"투표 참여/총 인원: {}/{}\n" # 20
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
#list_week_selected = [False, False, False, False, False, False, False]

list_command = [
    "create"
    ,"h"
    ,"f"
    ,"delete"
    ,"show"
]

dict_data = {}

CREATE, REPEAT, CHOOSE, CHOOSE_CHK, ASK, VOTE, ENSURE, FIX, PREACQ, COMP, FIX_TDAY, PREACQ2, ASK_CHK, KEEP_CHOOSE = range(14)

# 언어 설정
list_button = list_button_ko
list_message = list_message_ko

# { 채널 id: 현재상태... } list_channel.update(a=1)
list_channel = {}

def makebutton(index, text = None, value = ""):
    if text is None:
        if value == "":
            return [InlineKeyboardButton(list_button[index][0], callback_data=list_button[index][1])]
        else:
            return [InlineKeyboardButton(list_button[index][0], callback_data=value)]
    else:
        if value == "":
            return [InlineKeyboardButton(text, callback_data=list_button[index][1])]
        else:
            return [InlineKeyboardButton(text, callback_data=value)]

kairos_token = "1110549427:AAHYDs1Lo3zUmSUpprI_qN04m-ekRSfvhxw"
updater = Updater(kairos_token) #, use_context=True)

def hello(update, context):
    context.message.reply_text("got message!")

def create(update, context):
    reply_markup = InlineKeyboardMarkup([makebutton(0), makebutton(1)])
    context.message.reply_text(list_message[0], reply_markup=reply_markup)
    chat_id = context.message.chat_id
    
    #list_channel[chat_id] = 'create'
    #dict_data[chat_id] = {'repeat': 'n', 'week':['sun','tue'], 'state':'create'}
    #dict_data[chat_id]['week'].append('wed')
    #dict_data[chat_id]['week'].remove('sun')
    #context.message.reply_text("got message!")

    # save state
    dict_data[chat_id] = {'state':'create'}

    return REPEAT
    #return ConversationHandler.END

def repeat(update, context):
    query = context.callback_query
    chat_id = query.message.chat_id
    #list_channel[chat_id] = 'repeat'
    # save state
    dict_data[chat_id]['state'] = 'repeat'

    if query.data == "no":
        update.edit_message_text(
            chat_id=chat_id
            ,message_id=query.message.message_id
            ,text=list_message[1] # 생성 취소
        )
        del dict_data[chat_id]
        return ConversationHandler.END
    elif query.data == "yes":
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
    #list_channel[chat_id] = 'choose'
    # save state
    dict_data[chat_id]['state'] = 'choose'
    choose_msg = ""
    if query.data == "yes":
        choose_msg = list_message[12]
        dict_data[chat_id]['repeat'] = True
    elif query.data == "no":
        choose_msg = list_message[11]
        dict_data[chat_id]['repeat'] = False
    else:
        # 중간에 다시 설정하려고 할 때..
        pass
    # 실수는 용납하지 않는다.
    # else:
    #     reply_markup = InlineKeyboardMarkup([makebutton(0), makebutton(1)])
    #     context.message.reply_text(list_message[0], reply_markup=reply_markup)
    #     return CREATE
    dict_data[chat_id]['week'] = [False, False, False, False, False, False, False]
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
    #list_channel[chat_id] = 'choose_chk'
    # save state
    dict_data[chat_id]['state'] = 'choose_chk'

    if query.data == "ok":
        # check at least one checked
        list_true = [val for val in dict_data[chat_id]['week'] if val == True]

        if not list_true:
            update.edit_message_text(
                chat_id=chat_id
                ,message_id=query.message.message_id
                ,text=list_message[13] # 요일선택
            )
            reply_markup = InlineKeyboardMarkup([makebutton(6), makebutton(7),makebutton(8), makebutton(9),makebutton(10), makebutton(11),makebutton(12),makebutton(13)]) #, makebutton(2)]) 
            update.edit_message_reply_markup(
                chat_id=chat_id
                ,message_id=query.message.message_id
                ,reply_markup=reply_markup
            )
            return CHOOSE_CHK

        # save week
        # 
        dict_data[chat_id]['setweek'] = 'done'
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
    elif query.data == "keep_yes":
        dict_data[chat_id]['week'] = [False, False, False, False, False, False, False]
        reply_markup = InlineKeyboardMarkup([makebutton(6), makebutton(7),makebutton(8), makebutton(9),makebutton(10), makebutton(11),makebutton(12),makebutton(13)]) #, makebutton(2)]) 
    
        update.edit_message_text(text=list_message[13]
                                , chat_id=chat_id
                                , message_id=query.message.message_id
                                , reply_markup=reply_markup)
    elif query.data == "keep_no":
        #reply_markup = InlineKeyboardMarkup([makebutton(6), makebutton(7),makebutton(8), makebutton(9),makebutton(10), makebutton(11),makebutton(12),makebutton(13)]) #, makebutton(2)]) 
    
        update.edit_message_text(text="알겠습니다."
                                , chat_id=chat_id
                                , message_id=query.message.message_id)
                                #, reply_markup=reply_markup)
        #return ConversationHandler.END
    else:
        list_button_week = []
        week_index = list_week.index(query.data)
        if dict_data[chat_id]['week'][week_index] == False:
            dict_data[chat_id]['week'][week_index] = True
            for i in range(7):
                if dict_data[chat_id]['week'][i] == True:
                    list_button_week.append(makebutton(i + 6, "✔ " + list_button[i + 6][0]))
                else:
                    list_button_week.append(makebutton(i + 6))
            list_button_week.append(makebutton(13))
            reply_markup = InlineKeyboardMarkup(list_button_week) # 일월화수목금토확인
            #reply_markup = InlineKeyboardMarkup([makebutton(6), makebutton(7),makebutton(8), makebutton(9),makebutton(10), makebutton(11),makebutton(12),makebutton(13)]) # 일월화수목금토확인
            update.edit_message_text(text=list_message[13]
                                , chat_id=chat_id
                                , message_id=query.message.message_id
                                , reply_markup=reply_markup)
        else:
            #list_button[week_index + 6][0] = list_button[week_index + 6][0][2:]
            dict_data[chat_id]['week'][week_index] = False
            for i in range(7):
                if dict_data[chat_id]['week'][i] == True:
                    list_button_week.append(makebutton(i + 6, "✔ " + list_button[i + 6][0]))
                else:
                    list_button_week.append(makebutton(i + 6))
            list_button_week.append(makebutton(13))
            reply_markup = InlineKeyboardMarkup(list_button_week) # 일월화수목금토확인
            #reply_markup = InlineKeyboardMarkup([makebutton(6), makebutton(7),makebutton(8), makebutton(9),makebutton(10), makebutton(11),makebutton(12),makebutton(13)]) # 일월화수목금토확인
            update.edit_message_text(text=list_message[13]
                                , chat_id=chat_id
                                , message_id=query.message.message_id
                                , reply_markup=reply_markup)
    return CHOOSE_CHK


def ask(update, context):
    query = context.callback_query
    chat_id = query.message.chat_id
    #list_channel[chat_id] = 'ask'
    # save state
    dict_data[chat_id]['state'] = 'ask'
    dict_data[chat_id]['setdone'] = False
    dict_data[chat_id]['votecnt'] = 0
    dict_data[chat_id]['voted'] = []
    if query.data == "now":
        update.edit_message_text(
            chat_id=chat_id
            ,message_id=query.message.message_id
            ,text=list_message[5] # 투표하라
        )
        dict_data[chat_id]['setwhen'] = 'now'
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
        dict_data[chat_id]['setwhen'] = 'tday'
        #return ENSURE
        return ASK_CHK
    elif query.data == "end":
        update.edit_message_text(text="알겠습니다."
                                , chat_id=chat_id
                                , message_id=query.message.message_id)
                                #, reply_markup=reply_markup)
        #return ConversationHandler.END
    # elif query.data == "prev":
    #     return ASK

    # return VOTE
    #return ConversationHandler.END

def ask_chk(update, context):
    query = context.callback_query
    chat_id = query.message.chat_id
    #list_channel[chat_id] = 'ask_chk'
    # save state
    dict_data[chat_id]['state'] = 'ask_chk'
    if query.data == "now":
        update.edit_message_text(
            chat_id=chat_id
            ,message_id=query.message.message_id
            ,text=list_message[5] # 투표하라
        )
        dict_data[chat_id]['setwhen'] = 'now'
        
    return ConversationHandler.END

def vote(update, context):
    query = context.callback_query
    chat_id = query.message.chat_id
    #list_channel[chat_id] = 'vote'
    # save state
    dict_data[chat_id]['state'] = 'vote'
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
    #list_channel[chat_id] = 'ensure'
    # save state
    dict_data[chat_id]['state'] = 'ensure'
    update.edit_message_text(
        chat_id=chat_id
        ,message_id=query.message.message_id
        ,text=list_message[10] # 시간 설정 완료했으니 당일 알림 줄게
    )
    return ConversationHandler.END

def fix(update, context):
    query = context.callback_query
    chat_id = query.message.chat_id
    #list_channel[chat_id] = 'fix'
    # save state
    dict_data[chat_id]['state'] = 'fix'
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
    #list_channel[chat_id] = 'preacq'
    # save state
    dict_data[chat_id]['state'] = 'preacq'
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
    #list_channel[chat_id] = 'preacq2'
    # save state
    dict_data[chat_id]['state'] = 'preacq2'
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
        dict_data[chat_id]['preacq'] = True
        return COMP
    elif query.data == "no":
        update.edit_message_text(
            chat_id=chat_id
            ,message_id=query.message.message_id
            ,text=list_message[9] # 설정완료
        )
        dict_data[chat_id]['preacq'] = False
        return ConversationHandler.END
    elif query.data == "end":
        update.edit_message_text(text="알겠습니다."
                                , chat_id=chat_id
                                , message_id=query.message.message_id)
        #return ConversationHandler.END


def comp(update, context):
    query = context.callback_query
    chat_id = query.message.chat_id
    #list_channel[chat_id] = 'comp'
    # save state
    dict_data[chat_id]['state'] = 'comp'
    
    if query.data == 'cancel':
        dict_data[chat_id]['preacq'] = False
        update.edit_message_text(
            chat_id=chat_id
            ,message_id=query.message.message_id
            ,text=list_message[9] # 설정완료
        ) 
        return ConversationHandler.END  
    elif query.data == 'end':
        update.edit_message_text(text="알겠습니다."
                                , chat_id=chat_id
                                , message_id=query.message.message_id)
    else:
        dict_data[chat_id]['preacqtime'] = query.data
        update.edit_message_text(
            chat_id=chat_id
            ,message_id=query.message.message_id
            ,text=list_message[9] # 설정완료
        )   
        return ConversationHandler.END
    # reply_markup = InlineKeyboardMarkup([makebutton(0), makebutton(1), makebutton(2)])
    # update.edit_message_reply_markup(
    #     chat_id=query.message.chat_id
    #     ,message_id=query.message.message_id
    #     ,reply_markup=reply_markup
    # )
    

def fixtime_tday(update, context, args):
    chat_id = context.message.chat_id
    #list_channel[chat_id] = 'fixtime_tday'
    # save state
    dict_data[chat_id]['state'] = 'fixtime_tday'
    #if args[0] >= 0 and args[0] <= 23 then save, or show message and go fix_chk
    if args[0].isdigit():
        input_time = int(args[0])
        if 0 <= input_time and input_time <= 23:
            # save
            reply_markup = InlineKeyboardMarkup([makebutton(0), makebutton(1)]) #, makebutton(2)])
            context.message.reply_text(list_message[10].format(args[0]) + list_message[8], reply_markup=reply_markup) 
            # 시간 설정 완료했으니 당일 알림 줄게 # 미리알림 하쉴?
            dict_data[chat_id]['tdayalarmtime'] = input_time
            return PREACQ2
        else:
            context.message.reply_text(list_message[14].format('t')) # 제대로 입력하라고 했잖니 0-23
            return ConversationHandler.END
    else:
        context.message.reply_text(list_message[14].format('t')) # 제대로 입력하라고 했잖니 0-23
        return ConversationHandler.END

def forcefixtime(update, context, args):
    chat_id = context.message.chat_id
    #list_channel[chat_id] = 'forcefixtime'
    # save state
    dict_data[chat_id]['state'] = 'forcefixtime'
    #if args[0] >= 0 and args[0] <= 23 then save, or show message and go fix_chk
    input_time = int(args[0])
    if 0 <= input_time and input_time <= 23:
        # save
        # ㅅㄱ {} 시로 저장완료 미리알림 하쉴?
        reply_markup = InlineKeyboardMarkup([makebutton(0), makebutton(1)]) #, makebutton(2)])
        context.message.reply_text(list_message[7].format(args[0]) + list_message[8], reply_markup=reply_markup) 
        dict_data[chat_id]['setdone'] = True
        dict_data[chat_id]['alarmtime'] = input_time
        return PREACQ2
    else:
        context.message.reply_text(list_message[14].format('f')) # 제대로 입력하라고 했잖니 0-23
        return ConversationHandler.END

def votetime(update, context, args):
    chat_id = context.message.chat_id
    #list_channel[chat_id] = 'votetime'
    # save state
    # dict_data[chat_id]['state'] = 'votetime'
    dict_data[chat_id]['voted'] = {}
    input_time = int(args[0])
    sender_id = context.message.from_user.id
    if 0 <= input_time and input_time <= 23:
        member_count = context.message.bot.get_chat_members_count(chat_id)
        dict_data[chat_id]['voted'][sender_id] = input_time
        dict_data[chat_id]['votecnt'] = len(dict_data[chat_id]['voted'])
        # save
        if member_count == dict_data[chat_id]['votecnt'] + 1:
            determin_time = 0
            dict_data[chat_id]['setdone'] = True
            # 다수결 시간 값 가져오기
            determin_time = Counter([val for val in dict_data[chat_id]['voted'].values()]).most_common(1)[0][0]
            dict_data[chat_id]['alarmtime'] = determin_time
            reply_markup = InlineKeyboardMarkup([makebutton(0), makebutton(1)]) #, makebutton(2)])
            context.message.reply_text(list_message[7].format(args[0]) + list_message[8], reply_markup=reply_markup) 
            return PREACQ2
        else:
            # {} 시로 저장되었고, {} 명의 투표가 남았습니다. 17
            # "현재 상태: \n" 18
            #  "{}시: {}명\n" 19
            # 투표를 중복으로 했을 경우, 수정되도록. 사람 id 를 같이 저장할 것.
            # 채널의 인원과 vote 된 수를 비교하여 같으면 시간 설정
            context.message.reply_text(list_message[17].format(input_time, member_count - 1 - dict_data[chat_id]['votecnt'])) # 
            return ConversationHandler.END
    else:
        context.message.reply_text(list_message[14].format('h')) # 제대로 입력하라고 했잖니 0-23
        return ConversationHandler.END




def show(update, context):
    # 리스트에 채널명으로 검사해서 있으면 보여준다
    chat_id = context.message.chat_id
    if chat_id not in dict_data:
        context.message.reply_text("생성된 알림이 없습니다. /create 명령어로 알람을 생성할 수 있습니다.")
    else:
        # 상태 값에 따라서 보여주기..
        this_data = dict_data[chat_id]
        strtext = ""
        
        # 반복
        if 'repeat' in this_data:
            if this_data['repeat'] == True:
                strtext += "알림은 주마다 반복됩니다.\n"
            else:
                strtext += "알림은 주마다 반복되지 않는 일회성 알림입니다.\n"
            # 요일 설정 표시
            if 'setweek' in this_data:
                # 요일 formatting.
                this_week = [list_button[index + 6][0] for index, val in enumerate(this_data['week']) if val == True ] 
                strtext += "알림 요일은 {} 입니다.\n".format(','.join(this_week))

                if 'setwhen' in this_data:
                    if this_data['setwhen'] == 'now':
                        # 현재 투표 상태 표시
                        # 명 이 {} 시에 투표.
                        
                        # 투표 다 끝냈을때
                        #if 'setdone' in this_data:
                        if this_data['setdone'] == True:
                            strtext += "알람은 {}시로 설정되었습니다.\n".format(this_data['alarmtime'])
                            
                            if 'preacq' in this_data:
                                if this_data['preacq'] == True:
                                    if 'preacqtime' in this_data:
                                        preacq_value = [i[0] for i in list_button if i[1] == this_data['preacqtime']]
                                        strtext += "미리알림은 {} 입니다.\n".format(preacq_value[0])
                                        context.message.reply_text(strtext)
                                    else:
                                        strtext += "미리알림은 사용하시되 시간을 안정하셨군요.\n"
                                        
                                        # 3h 1h 30min 10min cancel
                                        reply_markup = InlineKeyboardMarkup([makebutton(14), makebutton(15),makebutton(16), makebutton(17), makebutton(18), makebutton(0, "지금은 안 할래요", "end")]) 
                                        
                                        context.message.reply_text(strtext + list_message[15], reply_markup=reply_markup)
                                else:
                                    strtext += "미리알림은 없습니다.\n"
                                    context.message.reply_text(strtext)
                            else:
                                strtext += "미리알림은 설정되어있지 않습니다.\n미리알림을 설정하시겠어요?\n"
                                # 미리알림 설정할래? 예 아니오 지금 안할래요.
                                reply_markup = InlineKeyboardMarkup([makebutton(0), makebutton(1), makebutton(0, "지금은 안 할래요", "end")]) #, makebutton(2)])
                                context.message.reply_text(strtext, reply_markup=reply_markup)
                        else:
                            if this_data['voted']:
                                strtext += list_message[18]
                                voted_result = Counter([val for val in this_data['voted'].values()]).most_common()
                                #determin_time = Counter([val for val in this_data['voted'].values()]).most_common(1)[0][0]
                                for index in range(0, len(voted_result)):
                                    strtext += list_message[19].format(voted_result[index][0], voted_result[index][1])
                            
                            # 참여인원
                            strtext += list_message[20].format(this_data['votecnt'], context.message.bot.get_chat_members_count(chat_id) - 1)

                            context.message.reply_text(strtext)
                    else:
                        # 당일 알림 시간 표시
                        if 'tdayalarmtime' in this_data:
                            strtext += "당일 투표알림은 {}시 입니다.\n".format(this_data['tdayalarmtime'])
                            if 'preacq' in this_data:
                                if this_data['preacq'] == True:
                                    if 'preacqtime' in this_data:
                                        strtext += "미리알림은 {}시 입니다.\n".format(this_data['preacqtime'])
                                        context.message.reply_text(strtext)
                                    else:
                                        strtext += "미리알림은 사용하시되 시간을 안정하셨군요.\n미리알림 시간을 설정하시겠어요?"
                                        
                                        # 3h 1h 30min 10min cancel
                                        reply_markup = InlineKeyboardMarkup([makebutton(14), makebutton(15),makebutton(16), makebutton(17), makebutton(18), makebutton(0, "지금은 안 할래요", "end")]) 
                                        
                                        context.message.reply_text(strtext + list_message[15], reply_markup=reply_markup)
                                else:
                                    strtext += "미리알림은 사용하지 않습니다.\n"
                                    context.message.reply_text(strtext)
                            else:
                                strtext += "미리알림은 설정되어있지 않습니다. \n미리알림을 설정하시겠어요?\n"
                                # 미리알림 설정할래? 예 아니오 지금 안할래요.
                                reply_markup = InlineKeyboardMarkup([makebutton(0), makebutton(1), makebutton(0, "지금은 안 할래요", "end")]) #, makebutton(2)])
                                context.message.reply_text(strtext, reply_markup=reply_markup)
                        else:
                            strtext += "당일 투표알림이 설정되었지만 시간은 설정되어있지 않네요.\n /t [0-23] 을 입력하여 설정해주세요.\n"
                            reply_markup = InlineKeyboardMarkup([makebutton(4)]) # 지금부터
                            context.message.reply_text(strtext + list_message[16], reply_markup=reply_markup)
                            
                else:
                    # 요일 설정 완료까지 한 상태 인데 당일알림인지 지금부터인지 투표시간은 안 정한 상태 (정했으면 위 setwhen에 걸렸음)
                    # 요일표시
                    # 당일알림/지금투표인지 설정하는 부분으로 이동
                    strtext += "투표시간을 정하는 중이시네요. 다시 이어가시겠어요?\n"
                    reply_markup = InlineKeyboardMarkup([makebutton(4), makebutton(5), makebutton(0, "지금은 안 할래요", "end")]) #, makebutton(2)])
                    context.message.reply_text(strtext, reply_markup=reply_markup)
            else:
                # 요일 설정까지 하다말았네
                strtext += "요일설정 중이시네요. 요일설정부터 다시 이어가시겠어요?\n"
                reply_markup = InlineKeyboardMarkup([makebutton(0, None, "keep_yes"), makebutton(1, None, "keep_no")]) #, makebutton(2)])
                context.message.reply_text(strtext, reply_markup=reply_markup)
            
        else:
            # 생성만 한 상태
            strtext += "알람이 생성만 되어있네요. /create 명령어로 다시 처음부터 시작해주세요.\n"
            context.message.reply_text(strtext)


def delete(update, context):
    # 리스트에 채널명으로 검사해서 있으면 삭제해주고 삭제했다고 메시지,
    # 없으면 생성된 것이 없다고 create로 생성할 수 있다고 메시지.
    chat_id = context.message.chat_id
    if chat_id not in dict_data:
        context.message.reply_text("생성된 알림이 없습니다. /create 명령어로 알람을 생성할 수 있습니다.")
    else:
        del dict_data[chat_id]
        context.message.reply_text("삭제하였습니다. /create 명령어로 알람을 다시 생성할 수 있습니다.")


def help(update, context):
    # 설명
    context.message.reply_text("/help : kairos 사용 명령어 표시\n/create : 알람 생성\n    /t : 당일에 투표할 시간 설정\n    /v [0-23(숫자)] : 알림 시간 투표\n    /f [0-23(숫자)] : 알림 시간 강제 설정\n/show : 현재 설정된 알람내용 보기\n/del : 설정된 알람 삭제") 

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
    ,allow_reentry=True
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

conv_handler4 = ConversationHandler(
    entry_points=[CommandHandler('v', votetime, pass_args=True)]
    ,states={
        PREACQ2: [CallbackQueryHandler(preacq2)]
        ,COMP: [CallbackQueryHandler(comp)]
        # ,FIX_TDAY: [CallbackQueryHandler(fixtime_tday)]
    }
    ,fallbacks=[CommandHandler('v', votetime, pass_args=True)]
)
updater.dispatcher.add_handler(conv_handler4)

#updater.dispatcher.add_handler(CommandHandler('f', forcefixtime, pass_args=True))
#updater.dispatcher.add_handler(CommandHandler('v', votetime, pass_args=True))
# updater.dispatcher.add_handler(CommandHandler('create', create))

updater.dispatcher.add_handler(CommandHandler('show', show))
# conv_handler5 = ConversationHandler(
#     entry_points=[CommandHandler('show', show)]
#     ,states={
#          CREATE: [CallbackQueryHandler(create)]
#         ,REPEAT: [CallbackQueryHandler(repeat)]
#         ,ASK: [CallbackQueryHandler(ask)]
#         ,ASK_CHK: [CallbackQueryHandler(ask_chk)]
#         ,VOTE: [CallbackQueryHandler(vote)]
#         #,ENSURE: [CallbackQueryHandler(ensure)]
#         #,FIX: [CallbackQueryHandler(fix)]
#         ,PREACQ: [CallbackQueryHandler(preacq)]
#         ,PREACQ2: [CallbackQueryHandler(preacq2)]
#         ,COMP: [CallbackQueryHandler(comp)]
#     }
#     ,fallbacks=[CommandHandler('show', show)]
#     ,allow_reentry=True
# )
# updater.dispatcher.add_handler(conv_handler5)


updater.dispatcher.add_handler(CommandHandler('del', delete))
updater.dispatcher.add_handler(CommandHandler('help', help))



print("start")
updater.start_polling()
updater.idle()
