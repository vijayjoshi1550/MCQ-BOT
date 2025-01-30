import pandas as pd
import telebot
import os
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF

# Bot token
API_TOKEN = 'YOUR TELEGRAM API TOKEN HERE'
bot = telebot.TeleBot(API_TOKEN)


def create_exam_pdf(directory, pdf_filename, num_questions=15):
    """
    Creates a PDF file with question images and question numbers.

    :param directory: Directory where the question images are stored.
    :param pdf_filename: Output PDF file name.
    :param num_questions: Number of questions to include in the PDF.
    """
    # Initialize the PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for i in range(1, num_questions + 1):
        image_path = os.path.join(directory, f"{i}.png")

        if os.path.exists(image_path):
            # Open the image
            img = Image.open(image_path)

            # Add a blank margin for question numbering
            img_with_text = Image.new("RGB", (img.width, img.height + 50), "white")
            img_with_text.paste(img, (0, 50))

            # Add the question number
            draw = ImageDraw.Draw(img_with_text)
            font = ImageFont.load_default()  # Default font
            text = f"Question {i}"
            draw.text((10, 10), text, fill="black", font=font)

            # Save the modified image temporarily
            temp_image_path = os.path.join(directory, f"temp_{i}.png")
            img_with_text.save(temp_image_path)

            # Add the image to the PDF
            pdf.add_page()
            pdf.image(temp_image_path, x=10, y=10, w=190)  # Resize image to fit PDF

            # Remove the temporary image
            os.remove(temp_image_path)
        else:
            print(f"Image for question {i} not found at {image_path}")

    # Save the PDF
    pdf.output(pdf_filename)
    print(f"PDF file '{pdf_filename}' created successfully!")


# Function to generate exam paper
def generate_exam_paper(user_id):
    # Create a folder (directory)
    folder_path = f"user_data/{str(user_id)}"
    os.makedirs(folder_path, exist_ok=True)  # Creates the folder, if it doesn't exist

    pdf_filename = f"{folder_path}/exam_questions.pdf"

    # Create the PDF file
    create_exam_pdf(directory="exam_ques", pdf_filename=pdf_filename, num_questions=15)

    # Send the PDF to the user
    with open(pdf_filename, 'rb') as pdf_file:
        bot.send_document(user_id, pdf_file, caption="📄 Here are the exam questions. Good luck! 🍀")

# Function to evaluate exam results
def evaluate_exam(user_id):
    # Create a folder (directory)
    folder_path = f"user_data/{str(user_id)}"
    os.makedirs(folder_path, exist_ok=True)  # Creates the folder, if it doesn't exist

    # Paths to the CSV files
    USER_DATA_FILE = f"{folder_path}/user_answers.csv"
    ANSWER_KEY_FILE = f"answer_key.csv"

    # Load the user answers and the answer key
    user_data = pd.read_csv(USER_DATA_FILE)
    answer_key = pd.read_csv(ANSWER_KEY_FILE)

    # Merge user answers with the answer key on question_no
    merged_df = pd.merge(user_data, answer_key, on='question_no', suffixes=('_user', '_correct'))

    # Compare answers and create a "result" column
    merged_df['is_correct'] = merged_df['answer_user'] == merged_df['answer_correct']

    # Calculate the number of correct answers
    correct_count = merged_df['is_correct'].sum()
    total_attempted = len(merged_df)
    total_questions = len(answer_key)

    # Create a result summary
    result_message = (
        f"📊 **Exam Results** 📊\n\n"
        f"✅ Correct Answers: {correct_count}/{total_questions}\n"
        f"❌ Incorrect Answers: {total_attempted - correct_count}/{total_questions}\n"
        f"📋 Unattempted Questions: {total_questions - total_attempted}\n\n"
        "💡 **Details**:\n"
    )

    # Add detailed feedback for each attempted question
    for _, row in merged_df.iterrows():
        question_no = row['question_no']
        user_answer = row['answer_user']
        correct_answer = row['answer_correct']
        if row['is_correct']:
            result_message += f"Question {question_no}: ✅ Correct \nCorrect Answer: ({user_answer})\n\n"
        else:
            result_message += f"Question {question_no}: ❌ Incorrect \n(Your Answer: {user_answer}, \nCorrect Answer: {correct_answer})\n\n"

    # Send the results to the user
    bot.send_message(user_id, result_message, parse_mode="Markdown")

    #delete user answer csv file
    if os.path.exists(USER_DATA_FILE):
        # Delete the file
        os.remove(USER_DATA_FILE)
