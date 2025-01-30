import telebot
import pandas as pd
import os

# Import user defined libraries
import recordans
import evaluation

# Replace 'YOUR_BOT_TOKEN' with your bot's API token
API_TOKEN = 'YOUR TELEGRAM API TOKEN HERE'
bot = telebot.TeleBot(API_TOKEN)

# Paths used in this python file
# mcq_csv_file variable


def delete_all_messages(user_id):

    folder_path = f"user_data/{str(user_id)}"

    # Load MCQ message IDs from the CSV file
    mcq_csv_file = f"{folder_path}/mcq_id.csv"

    # Read the CSV file
    df = pd.read_csv(mcq_csv_file)

    # Get the number of rows
    num_rows = df.shape[0]
    print(num_rows)

    #delete all user messages
    for i in range(1, num_rows + 1):
        try:
            # Extract message_id for the current question_no
            message_id = df.loc[df['question_no'] == i, 'message_id'].values[0]
            # Convert to integer (if not already)
            message_id = int(message_id)

            # Attempt to delete the user message
            bot.delete_message(chat_id=user_id, message_id=message_id)
            print(f"Message with ID {message_id} deleted successfully.")

        except IndexError:
            # Handle cases where the question_no is not found in the DataFrame
            print(f"Question number {i} not found in the CSV.")
        except telebot.apihelper.ApiTelegramException as e:
            # Handle Telegram-specific exceptions
            print(f"Failed to delete message with ID {message_id}. Error: {e}")
        except Exception as e:
            # General exception handling
            bot.send_message(
                user_id,
                f"There was an error while deleting message ID {message_id}: {e}"
            )
            print(f"Error while deleting message ID {message_id}: {e}")

    bot.send_message(user_id, "Exam Finished")
    bot.send_message(user_id, "Your exam has been successfully submitted. Thank you!")
    bot.send_message(user_id, "⏳ Please hold on...\nWe are currently calculating your result. "
                              "This will just take a moment!")
    evaluation.generate_exam_paper(user_id)
    evaluation.evaluate_exam(user_id)

    # Delete the file
    os.remove(mcq_csv_file)


def delete_one_messages(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id
    caption = call.message.caption.split("-", 2)
    question_no = caption[1]
    selected_option = call.data.split(" ", 2)  # The option selected by the user and split into matrices
    answer = selected_option[1]  # answer extracted from selected option
    # Record the answer
    if recordans.record_answer(user_id, message_id, question_no, answer):
        # Acknowledge the user's answer
        bot.answer_callback_query(call.id, f"You selected: {answer}")
        bot.delete_message(chat_id=user_id, message_id=message_id)
        # bot.send_message(user_id,
        #                  f"Your answer '{call.data}' for {call.message.caption} has been recorded.\n Thank you!")
    else:
        bot.send_message(user_id,
                         f"There is some error while recording the answer.")
