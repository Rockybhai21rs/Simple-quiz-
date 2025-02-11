import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Quiz data
QUIZ = [
    {"question": "What is the capital of France?", "answer": "Paris"},
    {"question": "What is 2 + 2?", "answer": "4"},
    {"question": "What is the largest planet in the solar system?", "answer": "Jupiter"},
]

# Start command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome to the Quiz Bot! Type /quiz to start.")

# Quiz command
async def quiz(update: Update, context: CallbackContext):
    context.user_data["score"] = 0
    context.user_data["current_question"] = 0
    await ask_question(update, context)

# Ask a question
async def ask_question(update: Update, context: CallbackContext):
    current_question = context.user_data["current_question"]
    if current_question < len(QUIZ):
        question = QUIZ[current_question]["question"]
        await update.message.reply_text(f"Question {current_question + 1}: {question}")
    else:
        await update.message.reply_text(f"Quiz over! Your score is {context.user_data['score']}/{len(QUIZ)}")

# Handle user answers
async def handle_answer(update: Update, context: CallbackContext):
    current_question = context.user_data["current_question"]
    user_answer = update.message.text.strip()
    correct_answer = QUIZ[current_question]["answer"]

    if user_answer.lower() == correct_answer.lower():
        context.user_data["score"] += 1
        await update.message.reply_text("Correct!")
    else:
        await update.message.reply_text(f"Wrong! The correct answer is {correct_answer}.")

    context.user_data["current_question"] += 1
    await ask_question(update, context)

# Main function
def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables.")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))

    app.run_polling()

if __name__ == "__main__":
    main()
