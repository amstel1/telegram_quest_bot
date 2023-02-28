from telegram.ext import Application, ConversationHandler, CallbackQueryHandler, CommandHandler, ContextTypes, PicklePersistence, MessageHandler
from telegram.ext import filters, JobQueue, CallbackContext


from telegram import Update, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from datetime import time
import pickle

from loguru import logger

gif_successful_links = []
gif_unsuccessful_links = []

response_correct = 'Верно! '
response_incorrect = 'Неверно. '

question_1 = 'Вопрос 1:'
question_1_hint_1 = 'Вопрос 1. Подсказка 1: . '
question_1_hint_2 = 'Вопрос 1. Подсказка 2: . '
answer_1 = 'Ответ 1: . '


question_2 = 'Вопрос 2: . '
question_2_reply_markup = InlineKeyboardMarkup(inline_keyboard=[[
                            InlineKeyboardButton(text='Опция 1 (верная)', callback_data='q2_ask1_correct'), 
                            InlineKeyboardButton(text='Опция 2 (неверная)', callback_data='q2_ask1_incorrect')
        ]])

question_2_hint_1 = 'Вопрос 2. Подсказка 1: . '
question_2_hint_1_reply_markup = InlineKeyboardMarkup(inline_keyboard=[[
                            InlineKeyboardButton(text='Опция 1 (верная)', callback_data='q2_ask2_correct'), 
                            InlineKeyboardButton(text='Опция 2 (неверная)', callback_data='q2_ask2_incorrect')
        ]])
question_2_hint_2 = 'Вопрос 2. Подсказка 2: . '
question_2_hint_2_reply_markup = InlineKeyboardMarkup(inline_keyboard=[[
                            InlineKeyboardButton(text='Опция 1 (верная)', callback_data='q2_ask3_correct'), 
                            InlineKeyboardButton(text='Опция 2 (неверная)', callback_data='q2_ask3_incorrect')
        ]])
answer_2 = 'Ответ 2: . '

quest_over = 'Вы завершили квест .'


async def callback_alarm(context: CallbackContext):
    logger.warning('GOOD, inside callback akarm')
    with open('./storage/store.pkl', 'rb') as f:
        persistence_file=pickle.load(f)
    chats = persistence_file.get('chat_data')
    for chat_id, chat_details in chats.items():
        await context.bot.send_message(
            chat_id=chat_id, 
            text='Hi, This is a daily reminder qwwewe'
        )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.effective_message
    chat = update.effective_chat
    chat_data = context.chat_data
    logger.info(f'{chat}')
    logger.info(f'{user}')
    logger.info(f'{message}')
    await chat.send_message('Helping')
    # await update.message.reply_text('Help2')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.effective_message
    chat = update.effective_chat
    chat_data = context.chat_data
    chat_data['previous_states'] = []
    chat_data['current_state'] = 'start'
    chat_data['previous_states'].append(chat_data['current_state'])

    await chat.send_message('Starting',
                       reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                            InlineKeyboardButton(text='Continue', callback_data='state_start_callback_ask_q1'), 
                            InlineKeyboardButton(text='End', callback_data='state_start_callback_end')
        ]])
    )
    # await update.message.reply_text('Starting2')  # shit

    await chat.send_message(text='Daily reminder has been set! You\'ll get notified at 10 AM daily')
    context.job_queue.run_daily(
        callback_alarm, 
        # context=update.message.chat_id,
        chat_id=chat.id,
        days=(0, 1, 2, 3, 4, 5, 6),
        time = time(hour = 15, minute = 11, second = 50)  # remember UTC time
    )
    logger.warning(context.job_queue)
    return 'state_start'

async def end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.effective_message
    chat = update.effective_chat
    chat_data = context.chat_data
    logger.info(f'{chat}_{user}_{message}')
    await chat.send_message('Ending')
    # await update.message.reply_text('Ending2')
    logger.info('implement here - express disappoinment user & Pickle Persistence')
    return ConversationHandler.END
 

# question handlers
async def q1_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = context.chat_data
    chat = update.effective_chat
    answer = update.callback_query
    if hasattr(answer, 'data'):
        # via callback
        callback_text = answer.data
        # logger.info(f'callback: {answer}')
        # logger.info(f'callback_text: {callback_text}')
        if callback_text == 'state_start_callback_ask_q1':
            chat_data['current_state'] = callback_text
            chat_data['previous_states'].append(chat_data['current_state'])
            logger.info('to do: congratulate user & gif success')
            await chat.send_message(question_1) #/ update.message.reply_text('Напишите гласную')
            return 'state_q1'
    else:
        # via text
        user_input = update.effective_message.text
        if chat_data.get('current_state') == 'state_start_callback_ask_q1':
            # Последнее действие - бот задал пользователю q1
            if user_input.lower() in list('aeouiаоеияюуыэ'):
                chat_data['current_state'] = 'state_q1_answer_a1'
                chat_data['previous_states'].append(chat_data['current_state'])
                await chat.send_message(response_correct + question_2, reply_markup=question_2_reply_markup)
                return 'state_q2'
            await chat.send_message(response_incorrect + question_1_hint_1)
            chat_data['current_state'] = 'state_q1_callback_q1_wrong_x1'
            chat_data['previous_states'].append(chat_data['current_state'])
            return 'state_q1'

        elif chat_data.get('current_state') == 'state_q1_callback_q1_wrong_x1':
            # сейчас второй неправильный ответ
            if user_input.lower() in list('aeouiаоеияюуыэ'):
                chat_data['current_state'] = 'state_q1_answer_a1'
                chat_data['previous_states'].append(chat_data['current_state'])
                await chat.send_message(response_correct + question_2, reply_markup=question_2_reply_markup)
                return 'state_q2'
            await chat.send_message(response_incorrect + question_1_hint_2)       
            chat_data['current_state'] = 'state_q1_callback_q1_wrong_x2'
            chat_data['previous_states'].append(chat_data['current_state'])
            return 'state_q1'
        
        elif chat_data.get('current_state') == 'state_q1_callback_q1_wrong_x2':
            # сейчас второй неправильный ответ
            if user_input.lower() in list('aeouiаоеияюуыэ'):
                chat_data['current_state'] = 'state_q1_answer_a1'
                chat_data['previous_states'].append(chat_data['current_state'])
                await chat.send_message(response_correct + question_2, reply_markup=question_2_reply_markup)
                return 'state_q2'
            await chat.send_message(response_incorrect + answer_1 + question_2, reply_markup=question_2_reply_markup)       
            return 'state_q2'
        





async def q2_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = context.chat_data
    chat = update.effective_chat
    answer = update.callback_query
    callback_text = answer.data
    
    if callback_text == 'q2_ask1_correct':
        chat_data['current_state'] = 'state_q2_callback_end'
        chat_data['previous_states'].append(chat_data['current_state'])
        await chat.send_message(response_correct + quest_over) 
        return 'state_q2'
    if callback_text == 'q2_ask1_incorrect':
        chat_data['current_state'] = callback_text
        chat_data['previous_states'].append(chat_data['current_state'])
        await chat.send_message(response_incorrect + question_2_hint_1, reply_markup=question_2_hint_1_reply_markup)  
        return 'state_q2'
    
    if callback_text == 'q2_ask2_correct':
        chat_data['current_state'] = 'state_q2_callback_end'
        chat_data['previous_states'].append(chat_data['current_state'])
        await chat.send_message(response_correct + quest_over) 
        return 'state_q2'
    if callback_text == 'q2_ask2_incorrect':
        chat_data['current_state'] = callback_text
        chat_data['previous_states'].append(chat_data['current_state'])
        await chat.send_message(response_incorrect + question_2_hint_2, reply_markup=question_2_hint_2_reply_markup)  
        return 'state_q2'
    
    if callback_text == 'q2_ask3_correct':
        chat_data['current_state'] = 'state_q2_callback_end'
        chat_data['previous_states'].append(chat_data['current_state'])
        await chat.send_message(response_correct + quest_over) 
        return 'state_q2'
    if callback_text == 'q2_ask3_incorrect':
        chat_data['current_state'] = callback_text
        chat_data['previous_states'].append(chat_data['current_state'])
        await chat.send_message(response_incorrect + answer_2 + quest_over)  
        return 'state_q2'

# def send_push_message_to_chat(app: Application):
#     bot = app.chat_data
#     logger.warning(bot)


# def reminder(update, context):
#    # bot.send_message(chat_id = update.effective_chat.id , text='Daily reminder has been set! You\'ll get notified at 8 AM daily')
#    context.job_queue.run_daily(
#     callback_alarm, 
#     context=update.message.chat_id,
#     days=(0, 1, 2, 3, 4, 5, 6),
#     time = time(hour = 17, minute = 52, second = 10)
# )

def main(): 
    storage = PicklePersistence(filepath='./storage/store.pkl')
    app = Application.builder().token('6181671111:AAFA8OiT0TN4wZm8R6AhqziHmt4VQIhiGwc').persistence(storage).build()
    #send_push_message_to_chat(app=app)

    start_handler = CommandHandler(command='start', callback=start)
    help_handler = CommandHandler(command='help', callback=help)
    conv_handler = ConversationHandler(
        entry_points=[start_handler],
        states={
            'state_start':[
                start_handler,
                CallbackQueryHandler(callback=q1_handler, pattern='^state_start_callback_ask_q1$'),  # continue & ask q1
                CallbackQueryHandler(callback=end, pattern='^state_start_callback_end$'),  # end   
            ],  
            # q1_handler
            'state_q1':[
                start_handler,
                MessageHandler(filters=filters.TEXT, callback=q1_handler),  # pseudo_callback
                CallbackQueryHandler(callback=q1_handler, pattern='^state_q1_callback_q1_wrong_x1$'),  # ask q1_wrong_x1
                CallbackQueryHandler(callback=q1_handler, pattern='^state_q1_callback_q1_wrong_x2$'),  # ask q1_wrong_x2
                CallbackQueryHandler(callback=q1_handler, pattern='^state_q1_callback_answer_a1$'),  # answer_a1 
            ],
            'state_q2':[
                start_handler,
                CallbackQueryHandler(callback=q2_handler, pattern='^q2_ask1_correct$'), 
                CallbackQueryHandler(callback=q2_handler, pattern='^q2_ask1_incorrect$'), 
                # CallbackQueryHandler(callback=q2_handler, pattern='^q2_ask2$'), 
                CallbackQueryHandler(callback=q2_handler, pattern='^q2_ask2_correct$'), 
                CallbackQueryHandler(callback=q2_handler, pattern='^q2_ask2_incorrect$'), 
                # CallbackQueryHandler(callback=q2_handler, pattern='^q2_ask3$'), 
                CallbackQueryHandler(callback=q2_handler, pattern='^q2_ask3_correct$'), 
                CallbackQueryHandler(callback=q2_handler, pattern='^q2_ask3_incorrect$'),

                CallbackQueryHandler(callback=end, pattern='^state_q2_callback_end$'),  # ask_q2
            ],            
         
        }, 
        fallbacks=[help_handler],
        persistent=True,
        name='the_conversation_handler',
    )

    app.add_handlers(handlers = [conv_handler, help_handler])
    app.run_polling()


if __name__ == "__main__":
    main()
