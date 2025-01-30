import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

# Import user defined libraries
import user_info
import schedule_time
import delete_msg
import os

#Creating Telegram Bot Object
Token = 'YOUR TELEGRAM API TOKEN HERE'
bot = telebot.TeleBot(Token)

# Dictionary to track user states
user_data = {}


# Function to delete necessary csv file
def delete_csv(user_id):
    folder_path = f"user_data/{str(user_id)}"

    # Load MCQ message IDs from the CSV file
    mcq_csv_file = f"{folder_path}/mcq_id.csv"
    user_answers = f"{folder_path}/user_answers.csv"
    exam_pdf = f"{folder_path}/exam_questions.pdf"

    if os.path.exists(mcq_csv_file):
        # Delete the file
        os.remove(mcq_csv_file)
    if os.path.exists(user_answers):
        # Delete the file
        os.remove(user_answers)
    if os.path.exists(exam_pdf):
        # Delete the file
        os.remove(exam_pdf)


# Start command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    delete_csv(user_id)  #deletes necessary csv file
    user_info.save_user_info(message.from_user)  # Save user info
    welcome_text = (
        "Welcome to the Examination System Bot! 📝\n\n"
        "You can use this bot to participate in exams.\n\n"
        "🤖 Bot programmed by:Vijay Joshi\n📱 Contact: @vijayjoshi098"
    )
    bot.reply_to(message, welcome_text)
    bot.send_message(user_id,
                     "Use the /schedule command to schedule exam that the bot will send to you at a specified time.\n\n")


# Start command
@bot.message_handler(commands=['schedule'])
def start(message):
    user_id = message.chat.id
    delete_csv(user_id)  #deletes necessary csv file
    # Optionally clear user data
    user_data.pop(user_id, None)
    user_id = message.chat.id
    user_data[user_id] = {}  # Create a temporary storage for the user
    bot.send_message(user_id, "Please enter the date in the format YYYY-MM-DD:")
    bot.register_next_step_handler(message, get_date)

# Function to handle date input
def get_date(message):
    user_id = message.chat.id
    try:
        # Parse and validate the date
        entered_date = datetime.strptime(message.text, "%Y-%m-%d").date()
        if entered_date < datetime.now().date():
            bot.send_message(user_id, "You cannot schedule a message for a past date. \nPlease enter a valid date:")
            bot.register_next_step_handler(message, get_date)  # Ask again
        else:
            user_data[user_id]['date'] = entered_date
            bot.send_message(user_id, "Now enter the time in the format HH:MM \n(24-hour format):")
            bot.register_next_step_handler(message, get_time)
    except ValueError:
        bot.send_message(user_id, "Invalid date format! \nPlease enter the date in the format YYYY-MM-DD:")
        bot.register_next_step_handler(message, get_date)  # Ask again

# Function to handle time input
def get_time(message):
    user_id = message.chat.id
    try:
        # Parse and validate the time
        entered_time = datetime.strptime(message.text, "%H:%M").time()
        scheduled_time = datetime.combine(user_data[user_id]['date'], entered_time)
        print(scheduled_time)
        if scheduled_time <= datetime.now():
            bot.send_message(user_id, "You cannot schedule your exam for past time. \nPlease enter a valid time again\n(24-hour format):")
            bot.register_next_step_handler(message, get_time)  # Ask again
        else:
            user_data[user_id]['time'] = entered_time
            # Schedule the message
            if schedule_time.schedule_message(message.chat.id, scheduled_time):
                # Exam Information
                topic = "Coulomb's Law"
                duration = "1 hour"
                additional_info = (
                    "📋 **Exam Guidelines**:\n"
                    "- You will have **1 hour** to complete the exam.\n"
                    "- The exam will automatically end after 1 hour.\n"
                    "- Please ensure a stable internet connection throughout the exam.\n"
                    f"- Your exam is scheduled to start at {scheduled_time}.\n\n"
                    "💡 **Tip**: Take your time and read each question carefully before answering!"
                )

                # Construct the exam message
                exam_info_message = (
                    f"🎓 **Exam Information** 🎓\n\n"
                    f"📚 **Topic**: {topic}\n"
                    f"⏳ **Duration**: {duration}\n\n"
                    f"{additional_info}\n"
                    "Good luck! 🍀"
                )

                # Send the message to the user
                bot.reply_to(message, f"Your exam has been scheduled for {str(scheduled_time)}")
                bot.send_message(user_id, exam_info_message, parse_mode="Markdown")
            else:
                bot.reply_to(message, "The scheduled time is in the past. \nPlease provide a valid time \n(24-hour format).")
    except ValueError:
        bot.send_message(user_id, "Invalid time format!\nPlease enter the time again in the format HH:MM:\n(24-hour format)")
        bot.register_next_step_handler(message, get_time)  # Ask again

# Callback for button clicks
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id

    if call.data == "submit_exam":
        # Ask for confirmation
        markup = InlineKeyboardMarkup()
        yes_button = InlineKeyboardButton("Yes", callback_data="confirm_submit")
        no_button = InlineKeyboardButton("No", callback_data="cancel_submit")
        markup.add(yes_button, no_button)
        bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
        sent_confirmation = bot.send_message(call.message.chat.id, "Are you sure you want to submit the exam?", reply_markup=markup)
        schedule_time.record_msg_id(user_id, sent_confirmation.message_id, 17)

    elif call.data == "confirm_submit":
        # Confirm exam submission
        bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
        try:
            delete_msg.delete_all_messages(user_id)
        except ValueError:
            bot.send_message(call.message.chat.id, "Error in deleting the message. Report it to developer")

    elif call.data == "cancel_submit":
        # Cancel exam submission
        bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, "Exam submission canceled.")
        schedule_time.send_submit_button(call.message.chat.id)

    else:
        delete_msg.delete_one_messages(call)


# Start polling
if __name__ == '__main__':
    print("Bot is running...")
    bot.infinity_polling()
