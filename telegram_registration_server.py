from telegram import Bot
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
import mysql.connector

db_config = {
    "host": "visionguarddb.cynkpxf20wc5.ap-south-1.rds.amazonaws.com",
    "user": "admin",
    "password": "9848Mysql",
    "database": "VisionGuardDB",
}

db_connection = mysql.connector.connect(**db_config)
db_cursor = db_connection.cursor()

bot = Bot(token='6449841998:AAHtJPCwWL55TzxtHnr1SJIzwg5BMnQHXQA')

WAITING_FOR_USERNAME, WAITING_FOR_PASSWORD = range(2)

def start(update, context):
    chat_id = update.message.chat_id
    bot.send_message(chat_id, "Please enter your username (without spaces):")
    return WAITING_FOR_USERNAME

def wait_for_username(update, context):
    user_message = update.message.text
    if ' ' in user_message:
        bot.send_message(update.message.chat_id, "Username cannot contain spaces. Please try again:")
        return WAITING_FOR_USERNAME
    context.user_data['username'] = user_message
    bot.send_message(update.message.chat_id, "Please enter your password (with at least one number, one special character, and both upper and lower case letters):")
    return WAITING_FOR_PASSWORD  

def wait_for_password(update, context):
    user_message = update.message.text
    if (
        not any(char.isdigit() for char in user_message) or
        not any(char.islower() for char in user_message) or
        not any(char.isupper() for char in user_message) or
        not any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?`~" for char in user_message)
    ):
        bot.send_message(update.message.chat_id, "Password requirements not met. Please try again:")
        return WAITING_FOR_PASSWORD
    
    context.user_data['password'] = user_message
    context.user_data['chat_id'] = update.message.from_user.id


    bot.send_message(update.message.chat_id, "Thank you! Your username and password have been recorded.")

    username = context.user_data['username']
    password = context.user_data['password']
    chat_id = context.user_data['chat_id']
    print(chat_id)
    insert_query = "INSERT INTO users (username, password, chat_id) VALUES (%s, %s, %s)"
    data = (username, password, chat_id)
    print(data)

    try:
        db_cursor.execute(insert_query, data)
        db_connection.commit()
        bot.send_message(update.message.chat_id, "Data saved to the database successfully.")
    except mysql.connector.Error as err:
        bot.send_message(update.message.chat_id, f"Error: {err}")
    '''finally:
        db_cursor.close()
        db_connection.close()'''

    return ConversationHandler.END  

def main():
    updater = Updater(token='6449841998:AAHtJPCwWL55TzxtHnr1SJIzwg5BMnQHXQA', use_context=True)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.command, start)],
        states={
            WAITING_FOR_USERNAME: [MessageHandler(Filters.text & ~Filters.command, wait_for_username)],
            WAITING_FOR_PASSWORD: [MessageHandler(Filters.text & ~Filters.command, wait_for_password)],
        },
        fallbacks=[],
    )
    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    try:
        main()
    finally:
        db_cursor.close()
        db_connection.close()
