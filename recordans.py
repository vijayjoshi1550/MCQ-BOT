import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import pandas as pd
import os
from datetime import datetime, timedelta


# Function to record answers in the CSV file
def record_answer(user_id, message_id, question_no, answer):
    # Create a folder (directory)
    folder_path = f"user_data/{str(user_id)}"
    os.makedirs(folder_path, exist_ok=True)  # Creates the folder, if it doesn't exist

    # Path for csv file
    csv_file = f"{folder_path}/user_answers.csv"

    # Create the CSV file if it doesn't exist
    if not os.path.exists(csv_file):
        df = pd.DataFrame(columns=["user_id", "message_id", "question_no", "answer"])
        df.to_csv(csv_file, index=False)

    new_entry = {
        "user_id": user_id,
        "message_id": message_id,
        "question_no": question_no,
        "answer": answer,
    }

    # Read the existing CSV file
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
    else:
        df = pd.DataFrame(columns=["user_id", "message_id", "question_no", "answer"])

    # Add the new entry to the DataFrame
    new_df = pd.DataFrame([new_entry])  # Create a new DataFrame from the entry
    df = pd.concat([df, new_df], ignore_index=True)

    # Save the updated DataFrame back to the CSV file
    df.to_csv(csv_file, index=False)
    print(f"Answer recorded: {new_entry}")

    return True

