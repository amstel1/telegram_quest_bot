DEBUG = True
from telegram.ext import Application, ConversationHandler, CallbackQueryHandler, CommandHandler, ContextTypes, PicklePersistence, MessageHandler
from telegram.ext import filters, JobQueue, CallbackContext
from telegram import Update, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from datetime import time
import pickle
from random import sample
from loguru import logger

gif_successful_links = []
gif_unsuccessful_links = []

response_correct = 'Верно! '
response_incorrect = 'Неверно. '

question_1 = '''
Привет! 
Наверное, тебе интересно, как так получилось, что на рабочем месте оказалась странная картинка с QR-кодом?
Порой ответы на вопросы невозможно получить просто так. А если попытаться найти ответы на все вопросы, то можно упустить важные детали…
Я пойду навстречу и дам подсказку. Отгадайте загадку и вы сможете начать командную игру. А потом, возможно, получите необходимые ответы для выигрыша.
«Ответ был на столе, лишь стоит присмотреться. Ты место найдешь там, где всегда занято и тихо. Принеси это обратно, пока растение не съело.»
'''
question_1_hint_1 = 'Найди место, где все отдыхают. '
question_1_hint_2 = 'Шифр там, где ты навела камеру '
answer_1 = '111273'


question_2 = 'Найди еще одну отгадку за машиной, которая рисует и клонирует'
question_2_reply_markup = InlineKeyboardMarkup(inline_keyboard=[[
                            InlineKeyboardButton(text='Нашел', callback_data='q2_correct'), 
                            InlineKeyboardButton(text='Не нашел', callback_data='q2_incorrect')
        ]])
question_2_hint_1 = 'Попробуйте еще. '
question_2_hint_1_reply_markup = InlineKeyboardMarkup(inline_keyboard=[[
                            InlineKeyboardButton(text='Нашел', callback_data='q2_h1_correct'), 
                            InlineKeyboardButton(text='Не нашел', callback_data='q2_h1_incorrect')
        ]])
question_2_hint_2 = 'Ну, пожалуйста.'
question_2_hint_2_reply_markup = InlineKeyboardMarkup(inline_keyboard=[[
                            InlineKeyboardButton(text='Нашел', callback_data='q2_h2_correct'), 
                            InlineKeyboardButton(text='Не нашел', callback_data='q2_h2_incorrect')
        ]])
answer_2 = 'Нашел - отлично, ты уже ближе к отгадке. Но сможешь ли ты разгадать все секреты? Я пришлю тебе загадку завтра в 12:00.'


question_3 = '''
Ты в начале пути. И вот твое первое задание на сегодня: «Дай мне ответ, какое время на часах может сделать квадрат, не пересекаясь и соединяясь воедино?»
'''
question_3_hint_1 = 'Это время на часах'
question_3_hint_2 = 'В этом времени все одинаковые цифры'
answer_3 = '11:11'


question_4 = '''
Отгадав загадку, ты получишь еще одну. Не на все вопросы можно получить ответы…
«Я вижу тебя, ты тоже меня видишь. Я хорошо тебя знаю и ты, смотря в меня, видишь себя». 
Найди меня. И возьми ключ к разгадке. Введи его здесь и мы пойдем дальше.
'''
question_4_hint_1 = 'Я не живое. '
question_4_hint_2 = 'Я показываю людей '
# проверяем == '841'
answer_4 = '841'
# post_answer_4 = '''
# Я прощаюсь с тобой до пятницы. Не пытайся додумать все самостоятельно. Следуй подсказкам.
# ''' 

question_5 = '''
Говорят, это Восьмое чудо света… Но так ли это? Найди меня в месте знаний на странице 37.
'''
question_5_hint_1 = 'Место, где читают книги. '
question_5_hint_2 = 'Что-то синее… '
answer_5 = '1137'


question_6 = '''Игры закончились… Тебя ждут серьёзные испытания в
будущем. Сможешь ли ты все разгадать?… Это вопрос. Но помни, что «счастье любит
тишину».'''  # тут так и должно быть
question_6_hint_1 = 'Счастье любит тишину… Не шуми '
question_6_hint_2 = 'Ты уже потеряла один ключ. Отгадать будет сложнее…'
answer_6 = ''  # я хз как это сделать



question_7 = '''
На выходных вы точно не думали, что вам нужно найти… Возможно, вы нарушили тишину и  я забрал у вас подсказку. Тем не менее, вы очень близки к тому, чтобы найти ключ от замка тайн.
«Я прячусь в том месте, где не выдерживают больше 20 минут. Оно больше. Люди меняются, они сменяются и есть там всегда. Я в желтой темноте. Вкусно. Найдите меня.
''' 

question_7_reply_markup = InlineKeyboardMarkup(inline_keyboard=[[
                            InlineKeyboardButton(text='Нашел', callback_data='q7_correct'), 
                            InlineKeyboardButton(text='Не нашел', callback_data='q7_incorrect')
        ]])
question_7_hint_1 = 'Желтая комната.'
question_7_hint_1_reply_markup = InlineKeyboardMarkup(inline_keyboard=[[
                            InlineKeyboardButton(text='Нашел', callback_data='q7_h1_correct'), 
                            InlineKeyboardButton(text='Не нашел', callback_data='q7_h1_incorrect')
        ]])
question_7_hint_2 = 'Где-то в полке.'
question_7_hint_2_reply_markup = InlineKeyboardMarkup(inline_keyboard=[[
                            InlineKeyboardButton(text='Нашел', callback_data='q7_h2_correct'), 
                            InlineKeyboardButton(text='Не нашел', callback_data='q7_h2_incorrect')
        ]])
answer_7 = 'Отлично!'


question_8 = '''
Ты действуешь на свою совесть. Если ты не нашла ключи, то и не найдешь. 
Вы работаете в команде и это правда. Оказывается, есть не только карьерные лестницы. 
Спорт.
'''
question_8_hint_1 = 'Ты можешь карабкаться. '
question_8_hint_2 = 'Это спортивная штука. '
# проверяем == '1'
answer_8 = '1'
post_answer = 'Сохрани ее. И не забудь завтра…'


question_9 = '''
Похоже на финал?.. У тебя есть предмет, который поможет разгадать загадку. 
«Если у тебя есть вредная привычка, то ты проведешь время с пользой. 
Возьми чистый лист и посмотри, что скрыто на нем при помощи света. Напиши мне, что ты видишь…».
'''
question_9_hint_1 = 'Речь идет про предметы. '
question_9_hint_2 = 'На этом рисуют и это горит. '
# проверяем == 
answer_9 = '9'
post_answer = 'Командная работа великолепна… Ищите меня в раздевалке за стеклом. И помните свой ответ…'

QUESTIONS = {
    1: question_1, 
    2: question_2, 
    3: question_3, 
    4: question_4, 
    5: question_5, 
    6: question_6, 
    7: question_7, 
    8: question_8, 
    9: question_9, 
}

ANSWERS = {
    1: answer_1, 
    2: answer_2, 
    3: answer_3, 
    4: answer_4, 
    5: answer_5, 
    6: answer_6, 
    7: answer_7, 
    8: answer_8, 
    9: answer_9, 
}

HINTS_1 = {
    1: question_1_hint_1,
    2: question_2_hint_1,
    3: question_3_hint_1,
    4: question_4_hint_1,
    5: question_5_hint_1,
    6: question_6_hint_1,
    7: question_7_hint_1,
    8: question_8_hint_1,
    9: question_9_hint_1,
}

HINTS_2 = {
    1: question_1_hint_2,
    2: question_2_hint_2,
    3: question_3_hint_2,
    4: question_4_hint_2,
    5: question_5_hint_2,
    6: question_6_hint_2,
    7: question_7_hint_2,
    8: question_8_hint_2,
    9: question_9_hint_2,
}

quest_over = 'Вы завершили квест. Но праздник продолжается!'



async def callback_alarm(context: CallbackContext):

    with open('./storage/store.pkl', 'rb') as f:
        persistence_file=pickle.load(f)
    chats = persistence_file.get('chat_data')
    for chat_id, chat_details in chats.items():
        current_state = chat_details.get('current_state')

        if current_state == 'q3':
            # пятница 14-20
            logger.warning(f'alarm q7: {chat_details}, {chat_id}')
            await context.bot.send_message(
                chat_id=chat_id, 
                text=question_3
            )
            return 'state_q3'

        if current_state == 'q6' or current_state == 'q7':
            # понедельник 9-30
            logger.warning(f'alarm q7: {chat_details}, {chat_id}')
            await context.bot.send_message(
                chat_id=chat_id, 
                text=question_7,
                reply_markup=question_7_reply_markup,
            )
            return 'state_q7'

        if current_state == 'q9':
            # вторник 9-00
            logger.warning(f'alarm q9: {chat_details}, {chat_id}')
            await context.bot.send_message(
                chat_id=chat_id, 
                text=question_9
            )
            return 'state_q9'


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.effective_message
    chat = update.effective_chat
    chat_data = context.chat_data
    logger.info(f'{chat}')
    logger.info(f'{user}')
    logger.info(f'{message}')
    await chat.send_message('Oops! Обратитесь к разработчикам')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info('start')
    user = update.effective_user
    message = update.effective_message
    chat = update.effective_chat
    chat_data = context.chat_data
    if 'current_state' not in chat_data:
        chat_data['current_state'] = 'start'
        await chat.send_message('Starting',
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                                InlineKeyboardButton(text='Continue', callback_data='q1'), 
                                InlineKeyboardButton(text='End', callback_data='end')
            ]])
        )

        logger.debug(f'Заводим расписание: callback_alarm, ')
        context.job_queue.run_daily(
            callback_alarm, 
            chat_id=chat.id,
            days=(4,), # пятница
            time = time(hour = 11, minute = 20, second = 1)  # remember UTC time, 14-20 минск
        )
        context.job_queue.run_daily(
            callback_alarm, 
            chat_id=chat.id,
            days=(0,), # понедельник
            time = time(hour = 6, minute = 30, second = 1)  # remember UTC time, 9-30 минск
        )
        context.job_queue.run_daily(
            callback_alarm, 
            chat_id=chat.id,
            days=(1,), # вторник
            time = time(hour = 6, minute = 0, second = 1)  # remember UTC time, 9-00 минск
        )
        return 'state_start'
    if 'current_state' in chat_data:
        current_state = chat_data.get('current_state')
        if current_state == 'start':
            await chat.send_message(question_1) 
            return 'state_q1'
        if current_state == 'q1':
            await chat.send_message(question_1) 
            return 'state_q1'
        if current_state == 'q2':
            await chat.send_message(question_2, reply_markup=question_2_reply_markup) 
            return 'state_q2'
        if current_state == 'q3':
            await chat.send_message(question_3) 
            return 'state_q3'
        if current_state == 'q4':
            await chat.send_message(question_4) 
            return 'state_q4'
        if current_state == 'q5':
            await chat.send_message(question_5) 
            return 'state_q5'
        if current_state == 'q6':
            await chat.send_message(question_7, reply_markup=question_7_reply_markup,) 
            return 'state_q7'
        if current_state == 'q7':
            await chat.send_message(question_7, reply_markup=question_7_reply_markup,) 
            return 'state_q7'
        if current_state == 'q8':
            await chat.send_message(question_8) 
            return 'state_q8'
        if current_state == 'q9':
            await chat.send_message(question_9) 
            return 'state_q9'


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.effective_message
    chat = update.effective_chat
    chat_data = context.chat_data
    logger.info(f'{chat}_{user}_{message}')
    await chat.send_message('Ending')
    logger.info('implement here')
    return ConversationHandler.END
 

# question handlers
async def q1_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''text handler'''
    q = 1
    chat_data = context.chat_data
    chat = update.effective_chat
    answer = update.callback_query
    user_input = update.effective_message.text
    current_state = chat_data.get('current_state')

    if current_state == 'start':
        chat_data['current_state'] = f'q{q}'
        await chat.send_message(QUESTIONS[q])
        return f'state_q{q}'
    
    if chat_data.get('current_state') == f'q{q}':
        if user_input.lower().strip() == ANSWERS[q]:
            chat_data['current_state'] = f'q{q+1}'
            await chat.send_message(response_correct)
            await chat.send_message(QUESTIONS[q+1], reply_markup=question_2_reply_markup)
            return f'state_q{q+1}'
        else:
            chat_data['current_state'] = f'q{q}_h1'
            await chat.send_message(response_incorrect + HINTS_1[q])
            return f'state_q{q}'

    elif current_state == f'q{q}_h1':
        # сейчас first hint
        if user_input.lower().strip() == ANSWERS[q]:
            chat_data['current_state'] = f'q{q+1}'
            await chat.send_message(response_correct + QUESTIONS[q+1], reply_markup=question_2_reply_markup)
            return f'state_q{q+1}'
        else:
            chat_data['current_state'] = f'q{q}_h2'
            await chat.send_message(response_incorrect + HINTS_2[q])       
            return f'state_q{q}'
        
    elif current_state == f'q{q}_h2':
        # сейчас second hint
        if user_input.lower().strip() == ANSWERS[q]:
            chat_data['current_state'] = f'q{q+1}'
            await chat.send_message(response_correct)
            await chat.send_message(QUESTIONS[q+1], reply_markup=question_2_reply_markup)
            return f'state_q{q+1}'
        else:
            chat_data['current_state'] = f'q{q+1}'
            await chat.send_message(response_incorrect + ANSWERS[q])   
            await chat.send_message(QUESTIONS[q+1], reply_markup=question_2_reply_markup)    
            return f'state_q{q+1}'
        

async def q2_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''keyboard handler'''
    q = 2
    chat_data = context.chat_data
    chat = update.effective_chat
    answer = update.callback_query
    callback_text = answer.data
    if callback_text == f'q{q}_correct':
        chat_data['current_state'] = f'q{q+1}'
        await chat.send_message(response_correct) 
        await chat.send_message(ANSWERS[q]) 
        if DEBUG:
            return ConversationHandler.END  # конец дня 1
        return f'state_q{q+1}'
        
    if callback_text == f'q{q}_incorrect':
        chat_data['current_state'] = f'q{q}'
        await chat.send_message(response_incorrect + HINTS_1[q], reply_markup=question_2_hint_1_reply_markup)  
        return f'state_q{q}'
    if callback_text == f'q{q}_h1_correct':
        chat_data['current_state'] = f'q{q+1}'
        await chat.send_message(response_correct) 
        await chat.send_message(ANSWERS[q]) 
        if DEBUG:
            return ConversationHandler.END  # конец дня 1
        return f'state_q{q+1}'
    if callback_text == f'q{q}_h1_incorrect':
        chat_data['current_state'] = f'q{q}'
        await chat.send_message(response_incorrect + HINTS_2[q], reply_markup=question_2_hint_2_reply_markup)  
        return f'state_q{q}'
    if callback_text == f'q{q}_h2_correct':
        chat_data['current_state'] = f'q{q+1}'
        await chat.send_message(response_correct) 
        await chat.send_message(ANSWERS[q]) 
        if DEBUG:
            return ConversationHandler.END  # конец дня 1
        return f'state_q{q+1}'
    if callback_text == f'q{q}_h2_incorrect':
        chat_data['current_state'] = f'q{q+1}'
        await chat.send_message(response_incorrect)  
        await chat.send_message(ANSWERS[q]) 
        if DEBUG:
            return ConversationHandler.END  # конец дня 1
        return f'state_q{q+1}'
        

async def q3_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''text handler'''
    q = 3
    chat_data = context.chat_data
    chat = update.effective_chat
    answer = update.callback_query
    user_input = update.effective_message.text
    current_state = chat_data.get('current_state')
    
    if chat_data.get('current_state') == f'q{q}':
        if user_input.lower().replace(' ','').replace('-','').replace(':','') == ANSWERS[q].replace(':',''):
            chat_data['current_state'] = f'q{q+1}'
            await chat.send_message(response_correct)
            await chat.send_message(QUESTIONS[q+1],)
            return f'state_q{q+1}'
        else:
            chat_data['current_state'] = f'q{q}_h1'
            await chat.send_message(response_incorrect + HINTS_1[q])
            return f'state_q{q}'

    elif current_state == f'q{q}_h1':
        if user_input.lower().replace(' ','').replace('-','').replace(':','') == ANSWERS[q].replace(':',''):
            chat_data['current_state'] = f'q{q+1}'
            await chat.send_message(response_correct + QUESTIONS[q+1],)
            return f'state_q{q+1}'
        else:
            chat_data['current_state'] = f'q{q}_h2'
            await chat.send_message(response_incorrect + HINTS_2[q])       
        return f'state_q{q}'
        
    elif current_state == f'q{q}_h2':
        if user_input.lower().replace(' ','').replace('-','').replace(':','') == ANSWERS[q].replace(':',''):
            chat_data['current_state'] = f'q{q+1}'
            await chat.send_message(response_correct)
            await chat.send_message(QUESTIONS[q],)
            return f'state_q{q+1}'
        else:
            chat_data['current_state'] = f'q{q+1}'
            await chat.send_message(response_incorrect + ANSWERS[q])   
            await chat.send_message(QUESTIONS[q],)    
        return f'state_q{q+1}'


async def q4_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''text handler'''
    q = 4
    chat_data = context.chat_data
    chat = update.effective_chat
    answer = update.callback_query
    user_input = update.effective_message.text
    current_state = chat_data.get('current_state')

    if chat_data.get('current_state') == f'q{q}':
        if user_input.lower().replace(' ','').replace('-','').replace(':','') == ANSWERS[q].replace(':',''):
            chat_data['current_state'] = f'q{q+1}'
            await chat.send_message(response_correct)
            await chat.send_message(QUESTIONS[q+1],)
            return f'state_q{q+1}'
        else:
            chat_data['current_state'] = f'q{q}_h1'
            await chat.send_message(response_incorrect + HINTS_1[q])
            return f'state_q{q}'

    elif current_state == f'q{q}_h1':
        if user_input.lower().replace(' ','').replace('-','').replace(':','') == ANSWERS[q].replace(':',''):
            chat_data['current_state'] = f'q{q+1}'
            await chat.send_message(response_correct + QUESTIONS[q+1],)
            return f'state_q{q+1}'
        else:
            chat_data['current_state'] = f'q{q}_h2'
            await chat.send_message(response_incorrect + HINTS_2[q])       
            return f'state_q{q}'
        
    elif current_state == f'q{q}_h2':
        if user_input.lower().replace(' ','').replace('-','').replace(':','') == ANSWERS[q].replace(':',''):
            chat_data['current_state'] = f'q{q+1}'
            await chat.send_message(response_correct)
            await chat.send_message(QUESTIONS[q+1],)
            return f'state_q{q+1}'
        else:
            chat_data['current_state'] = f'q{q+1}'
            await chat.send_message(response_incorrect + ANSWERS[q])   
            await chat.send_message(QUESTIONS[q+1],)    
            return f'state_q{q+1}'



async def q5_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''text handler'''
    q = 5
    chat_data = context.chat_data
    chat = update.effective_chat
    answer = update.callback_query
    user_input = update.effective_message.text
    current_state = chat_data.get('current_state')
    
    if chat_data.get('current_state') == f'q{q}':
        if user_input.lower().replace(' ','').replace('-','').replace(':','') == ANSWERS[q].replace(':',''):
            chat_data['current_state'] = f'q{q+1}'
            await chat.send_message(response_correct)
            await chat.send_message(QUESTIONS[q+1],)
            return f'state_q{q+1}'
        else:
            chat_data['current_state'] = f'q{q}_h1'
            await chat.send_message(response_incorrect + HINTS_1[q])
            return f'state_q{q}'

    elif current_state == f'q{q}_h1':
        if user_input.lower().replace(' ','').replace('-','').replace(':','') == ANSWERS[q].replace(':',''):
            chat_data['current_state'] = f'q{q+1}'
            await chat.send_message(response_correct + QUESTIONS[q+1],)
            return f'state_q{q+1}'
        else:
            chat_data['current_state'] = f'q{q}_h2'
            await chat.send_message(response_incorrect + HINTS_2[q])       
            return f'state_q{q}'
        
    elif current_state == f'q{q}_h2':
        if user_input.lower().replace(' ','').replace('-','').replace(':','') == ANSWERS[q].replace(':',''):
            chat_data['current_state'] = f'q{q+1}'
            await chat.send_message(response_correct)
            await chat.send_message(QUESTIONS[q+1],)
            return f'state_q{q+1}'
        else:
            chat_data['current_state'] = f'q{q+1}'
            await chat.send_message(response_incorrect + ANSWERS[q])   
            await chat.send_message(QUESTIONS[q+1],)    
            return f'state_q{q+1}'


async def q6_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''text handler'''
    q = 6
    chat_data = context.chat_data
    chat = update.effective_chat
    answer = update.callback_query
    user_input = update.effective_message.text
    current_state = chat_data.get('current_state')
    
    if chat_data.get('current_state') == f'q{q}':
        if user_input.lower().replace('-','').replace(':','') == ANSWERS[q].replace(':',''):
            chat_data['current_state'] = f'q{q+1}'
            await chat.send_message(response_correct)
            await chat.send_message(QUESTIONS[q+1], reply_markup=question_7_reply_markup)
            if DEBUG:
                return ConversationHandler.END  # конец дня 1
            return f'state_q{q+1}'
        else:
            chat_data['current_state'] = f'q{q}_h1'
            await chat.send_message(response_incorrect + HINTS_1[q])
            return f'state_q{q}'

    elif current_state == f'q{q}_h1':
        if user_input.lower().replace('-','').replace(':','') == ANSWERS[q].replace(':',''):
            chat_data['current_state'] = f'q{q+1}'
            if DEBUG:
                return ConversationHandler.END  # конец дня 1
            await chat.send_message(response_correct + QUESTIONS[q+1], reply_markup=question_7_reply_markup)
            return f'state_q{q+1}'
        else:
            chat_data['current_state'] = f'q{q}_h2'
            await chat.send_message(response_incorrect + HINTS_2[q])       
            return f'state_q{q}'
        
    elif current_state == f'q{q}_h2':
        if user_input.lower().replace('-','').replace(':','') == ANSWERS[q].replace(':',''):
            chat_data['current_state'] = f'q{q+1}'
            await chat.send_message(response_correct)
            if DEBUG:
                return ConversationHandler.END  # конец дня 1
            await chat.send_message(QUESTIONS[q+1], reply_markup=question_7_reply_markup)
            return f'state_q{q+1}'
        else:
            chat_data['current_state'] = f'q{q+1}'
            await chat.send_message(response_incorrect + ANSWERS[q])   
            if DEBUG:
                return ConversationHandler.END  # конец дня 1
            await chat.send_message(QUESTIONS[q+1], reply_markup=question_7_reply_markup)  
            return f'state_q{q+1}'


async def q7_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''keyboard handler'''
    q = 7
    chat_data = context.chat_data
    chat = update.effective_chat
    answer = update.callback_query
    callback_text = answer.data
    if callback_text == f'q{q}_correct':
        chat_data['current_state'] = f'q{q+1}'
        await chat.send_message(ANSWERS[q]) 
        await chat.send_message(QUESTIONS[q+1]) 
        return f'state_q{q+1}'
    if callback_text == f'q{q}_incorrect':
        chat_data['current_state'] = f'q{q}'
        await chat.send_message(response_incorrect + HINTS_1[q], reply_markup=question_7_hint_1_reply_markup)  
        return f'state_q{q}'
    if callback_text == f'q{q}_h1_correct':
        chat_data['current_state'] = f'q{q+1}'
        await chat.send_message(ANSWERS[q]) 
        await chat.send_message(QUESTIONS[q+1]) 
        return f'state_q{q+1}'
    if callback_text == f'q{q}_h1_incorrect':
        chat_data['current_state'] = f'q{q}'
        await chat.send_message(response_incorrect + HINTS_2[q], reply_markup=question_7_hint_2_reply_markup)  
        return f'state_q{q}'
    if callback_text == f'q{q}_h2_correct':
        chat_data['current_state'] = f'q{q+1}'
        await chat.send_message(ANSWERS[q]) 
        await chat.send_message(QUESTIONS[q+1]) 
        return f'state_q{q+1}'
    if callback_text == f'q{q}_h2_incorrect':
        chat_data['current_state'] = f'q{q+1}'
        await chat.send_message(response_incorrect)  
        await chat.send_message(ANSWERS[q]) 
        await chat.send_message(QUESTIONS[q+1]) 
        return f'state_q{q+1}'


async def q8_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''text handler'''
    q = 8
    chat_data = context.chat_data
    chat = update.effective_chat
    answer = update.callback_query
    user_input = update.effective_message.text
    current_state = chat_data.get('current_state')
    
    if chat_data.get('current_state') == f'q{q}':
        if user_input.lower().replace(' ','').replace('-','').replace(':','') == ANSWERS[q].replace(':',''):
            chat_data['current_state'] = f'q{q+1}'
            await chat.send_message(response_correct)
            await chat.send_message(post_answer)
            if DEBUG:
                return ConversationHandler.END  # конец дня 1
            return f'state_q{q+1}'
        else:
            chat_data['current_state'] = f'q{q}_h1'
            await chat.send_message(response_incorrect + HINTS_1[q])
            return f'state_q{q}'

    elif current_state == f'q{q}_h1':
        if user_input.lower().replace(' ','').replace('-','').replace(':','') == ANSWERS[q].replace(':',''):
            chat_data['current_state'] = f'q{q+1}'
            if DEBUG:
                return ConversationHandler.END  # конец дня 1
            return f'state_q{q+1}'
        else:
            chat_data['current_state'] = f'q{q}_h2'
            await chat.send_message(response_incorrect + HINTS_2[q])       
            return f'state_q{q}'
        
    elif current_state == f'q{q}_h2':
        if user_input.lower().replace(' ','').replace('-','').replace(':','') == ANSWERS[q].replace(':',''):
            chat_data['current_state'] = f'q{q+1}'
            await chat.send_message(response_correct)
            await chat.send_message(post_answer)
            if DEBUG:
                return ConversationHandler.END  # конец дня 1
            return f'state_q{q+1}'
        else:
            chat_data['current_state'] = f'q{q+1}'
            await chat.send_message(response_incorrect + ANSWERS[q])  
            await chat.send_message(post_answer)
            if DEBUG:
                return ConversationHandler.END  # конец дня 1
            return f'state_q{q+1}'

     
async def q9_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''text handler'''
    q = 9
    chat_data = context.chat_data
    chat = update.effective_chat
    answer = update.callback_query
    user_input = update.effective_message.text
    current_state = chat_data.get('current_state')
    
    if chat_data.get('current_state') == f'q{q}':
        if user_input.lower().replace(' ','').replace('-','').replace(':','') == ANSWERS[q].replace(':',''):
            chat_data['current_state'] = f'q{q+1}'
            await chat.send_message(response_correct)
            await chat.send_message(post_answer) 
            await chat.send_message(quest_over)        
            return f'state_q{q+1}'
        else:
            chat_data['current_state'] = f'q{q}_h1'
            await chat.send_message(response_incorrect + HINTS_1[q])
            return f'state_q{q}'

    elif current_state == f'q{q}_h1':
        if user_input.lower().replace(' ','').replace('-','').replace(':','') == ANSWERS[q].replace(':',''):
            chat_data['current_state'] = f'q{q+1}'
            await chat.send_message(response_correct)
            await chat.send_message(post_answer) 
            await chat.send_message(quest_over)        
            ConversationHandler.END
        else:
            chat_data['current_state'] = f'q{q}_h2'
            await chat.send_message(response_incorrect + HINTS_2[q])       
            return f'state_q{q}'
        
    elif current_state == f'q{q}_h2':
        if user_input.lower().replace(' ','').replace('-','').replace(':','') == ANSWERS[q].replace(':',''):
            chat_data['current_state'] = f'q{q+1}'
            await chat.send_message(response_correct)
            await chat.send_message(post_answer) 
            await chat.send_message(quest_over)        
            return ConversationHandler.END
        else:
            chat_data['current_state'] = f'q{q+1}'
            await chat.send_message(response_incorrect + ANSWERS[q])   
            await chat.send_message(post_answer) 
            await chat.send_message(quest_over)        
            return ConversationHandler.END


def main(): 
    storage = PicklePersistence(filepath='./storage/store.pkl')
    app = Application.builder().token('6181671111:AAFA8OiT0TN4wZm8R6AhqziHmt4VQIhiGwc').persistence(storage).build()

    start_handler = CommandHandler(command='start', callback=start)
    help_handler = CommandHandler(command='help', callback=help)
    conv_handler = ConversationHandler(
        entry_points=[start_handler],
        states={
            'state_start':[
                start_handler,
                CallbackQueryHandler(callback=q1_handler, pattern='^q1$'),  # continue & ask q1
                CallbackQueryHandler(callback=end, pattern='^end$'),  # end   
            ],  
            # q1_handler
            'state_q1':[
                start_handler,
                CallbackQueryHandler(callback=q1_handler, pattern='^q1$'),  # continue & ask q1
                MessageHandler(filters=filters.TEXT, callback=q1_handler),  # pseudo_callback
                #CallbackQueryHandler(callback=q1_handler, pattern='^q1_h1$'),  # ask q1_wrong_x1
                #CallbackQueryHandler(callback=q1_handler, pattern='^q1_h2$'),  # ask q1_wrong_x2
                # CallbackQueryHandler(callback=q1_handler, pattern='^q2$'),  # answer_a1 
            ],

            'state_q2':[
                start_handler,
                CallbackQueryHandler(callback=q2_handler, pattern='^q2_correct$'), 
                CallbackQueryHandler(callback=q2_handler, pattern='^q2_incorrect$'), 
                CallbackQueryHandler(callback=q2_handler, pattern='^q2_h1_correct$'), 
                CallbackQueryHandler(callback=q2_handler, pattern='^q2_h1_incorrect$'), 
                CallbackQueryHandler(callback=q2_handler, pattern='^q2_h2_correct$'), 
                CallbackQueryHandler(callback=q2_handler, pattern='^q2_h2_incorrect$'),
                CallbackQueryHandler(callback=q2_handler, pattern='^q3$'),
            ], 

            'state_q3':[
                start_handler,
                MessageHandler(filters=filters.TEXT, callback=q3_handler),  # pseudo_callback
            ], 

            'state_q4':[
                start_handler,
                MessageHandler(filters=filters.TEXT, callback=q4_handler),  # pseudo_callback
            ], 

            'state_q5':[
                start_handler,
                MessageHandler(filters=filters.TEXT, callback=q5_handler),  # pseudo_callback
            ], 

            'state_q6':[
                start_handler,
                MessageHandler(filters=filters.TEXT, callback=q6_handler),  # pseudo_callback
            ], 

            'state_q7':[
                start_handler,
                CallbackQueryHandler(callback=q7_handler, pattern='^q7_correct$'), 
                CallbackQueryHandler(callback=q7_handler, pattern='^q7_incorrect$'), 
                CallbackQueryHandler(callback=q7_handler, pattern='^q7_h1_correct$'), 
                CallbackQueryHandler(callback=q7_handler, pattern='^q7_h1_incorrect$'), 
                CallbackQueryHandler(callback=q7_handler, pattern='^q7_h2_correct$'), 
                CallbackQueryHandler(callback=q7_handler, pattern='^q7_h2_incorrect$'),
                CallbackQueryHandler(callback=q7_handler, pattern='^q8$'),
            ], 

            'state_q8':[
                start_handler,
                MessageHandler(filters=filters.TEXT, callback=q8_handler),  # pseudo_callback
            ], 

            'state_q9':[
                start_handler,
                MessageHandler(filters=filters.TEXT, callback=q9_handler),  # pseudo_callback
            ], 

            ConversationHandler.END:[
                start_handler,
                CallbackQueryHandler(callback=end, pattern='^end$'),  # end   
            ], 
         
        }, 
        fallbacks=[help_handler],
        persistent=True,
        name='the_conversation_handler',
    )

    app.add_handlers(handlers = [conv_handler, help_handler])
    app.run_polling(poll_interval=1.0, timeout=150)


if __name__ == "__main__":
    main()
