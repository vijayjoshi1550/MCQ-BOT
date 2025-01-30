import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import pandas as pd
import os
import threading
from datetime import datetime, timedelta
import time

#Import user defined python files
import delete_msg

#Creating Telegram Bot Object
Token = 'YOUR TELEGRAM API TOKEN HERE'
bot = telebot.TeleBot(Token)


# Paths used in this python file
# MCQ_ID_CSV_FILE variable


# Function to schedule a message with an optional image
def schedule_message(chat_id, scheduled_time):
    now = datetime.now()
    delay = (scheduled_time - now).total_seconds()

    if delay > 0:
        print(f"Message scheduled for {scheduled_time}")
        # Pass chat_id as a tuple in args
        threading.Timer(delay, send_scheduled_message, args=(chat_id,)).start()
        return True
    else:
        return False


# Function to send a scheduled message with an optional image
def send_scheduled_message(chat_id):
    # Send Questions to user
    for i in range(1, 16):
        # Add inline buttons for options
        markup = InlineKeyboardMarkup()
        options = ["Option A", "Option B", "Option C", "Option D"]
        for option in options:
            markup.add(InlineKeyboardButton(option, callback_data=option))

        # Send Questions to user
        try:
            with open(f"exam_ques/{i}.PNG", "rb") as image:
                sent_photo = bot.send_photo(chat_id, photo=image, caption=f"Question-{i}", reply_markup=markup)
                print(f"Sent scheduled message with image to {chat_id}")
        except FileNotFoundError:
            bot.send_message(chat_id, f"Question image {i}.PNG not found.")
            continue
        record_msg_id(chat_id, sent_photo.message_id, i)

    # Send Submit button
    send_submit_button(chat_id)

    # Starting exam timer of 1 hour
    threading.Timer(3600, time_over, args=(chat_id,)).start()

    # Create User Answer CSV File

    # Create a folder (directory)
    folder_path = f"user_data/{str(chat_id)}"
    os.makedirs(folder_path, exist_ok=True)  # Creates the folder, if it doesn't exist

    # Path for csv file
    csv_file = f"{folder_path}/user_answers.csv"

    # Create the CSV file if it doesn't exist
    if not os.path.exists(csv_file):
        df = pd.DataFrame(columns=["user_id", "message_id", "question_no", "answer"])
        df.to_csv(csv_file, index=False)


# Function to send submit button
def send_submit_button(chat_id):
    # Create an inline keyboard with the "Submit Exam" button
    markup = InlineKeyboardMarkup()
    submit_button = InlineKeyboardButton("Submit Exam", callback_data="submit_exam")
    markup.add(submit_button)

    # Send the inline keyboard to the user
    sent_submit = bot.send_message(chat_id, "Click the button below to submit your exam:", reply_markup=markup)
    record_msg_id(chat_id, sent_submit.message_id, 16)


def time_over(chat_id):
    delete_msg.delete_all_messages(chat_id)


# Function to record the message-id
def record_msg_id(chat_id, message_id, question_num):
    # Create a folder (directory)
    folder_path = f"user_data/{str(chat_id)}"
    os.makedirs(folder_path, exist_ok=True)  # Creates the folder, if it doesn't exist

    # Path for CSV file
    MCQ_ID_CSV_FILE = f"{folder_path}/mcq_id.csv"

    # Read or initialize the DataFrame
    if os.path.exists(MCQ_ID_CSV_FILE):
        df = pd.read_csv(MCQ_ID_CSV_FILE)
    else:
        df = pd.DataFrame(columns=["user_id", "message_id", "question_no"])

    # Check if the question number already exists
    if question_num in df['question_no'].values:
        # Update the existing entry
        df.loc[df['question_no'] == question_num, ['message_id']] = message_id
        print(f"Updated question {question_num} with message_id {message_id}")
    else:
        # Add a new entry
        new_entry = {
            "user_id": chat_id,
            "message_id": message_id,
            "question_no": question_num,
        }
        new_df = pd.DataFrame([new_entry])  # Create a new DataFrame from the entry
        df = pd.concat([df, new_df], ignore_index=True)
        print(f"Added new question {question_num} with message_id {message_id}")
        print(f"MCQ Data recorded: {new_entry}")

    # Save the updated DataFrame back to the CSV file
    df.to_csv(MCQ_ID_CSV_FILE, index=False)
