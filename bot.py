import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import uuid

# Generate a unique quiz ID
def generate_quiz_id():
    return str(uuid.uuid4())

# Share quiz command
async def share_quiz(update: Update, context: CallbackContext):
    quiz_id = generate_quiz_id()
    quiz_link = f"https://t.me/your_bot_username?start=quiz_{quiz_id}"
    await update.message.reply_text(f"Share this link to invite others to take the quiz: {quiz_link}")

# Load environment variables
load_dotenv()

# Dummy HTTP server
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_server():
    server = HTTPServer(("0.0.0.0", 8080), DummyServer)
    server.serve_forever()

# Quiz data storage (in-memory for simplicity)
quizzes = {}

# Start command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Welcome to Quiz Bot! Use /create to start creating a quiz."
    )

# Create quiz command
async def create_quiz(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Let's create a new quiz. First, send me the title of your quiz (e.g., 'Aptitude Test')."
    )
    context.user_data["step"] = "title"

# Handle quiz creation steps
async def handle_message(update: Update, context: CallbackContext):
    step = context.user_data.get("step")
    user_id = update.message.from_user.id

    if step == "title":
        context.user_data["title"] = update.message.text
        await update.message.reply_text(
            "Great! Now send me a description of your quiz (or /skip to skip this step)."
        )
        context.user_data["step"] = "description"

    elif step == "description":
        if update.message.text.lower() != "/skip":
            context.user_data["description"] = update.message.text
        await update.message.reply_text(
            "Now send me your first question (e.g., 'What is CPU?')."
        )
        context.user_data["step"] = "question"

    elif step == "question":
        question = update.message.text
        quizzes[user_id] = {"title": context.user_data["title"], "description": context.user_data.get("description"), "questions": [question]}
        await update.message.reply_text(
            f"Question added: {question}\nUse /add to add more questions or /finish to complete the quiz."
        )
        context.user_data["step"] = "add_questions"

    elif step == "add_questions":
        if update.message.text.lower() == "/finish":
            await update.message.reply_text(
                f"Quiz created successfully!\nTitle: {context.user_data['title']}\nDescription: {context.user_data.get('description', 'No description')}\nQuestions: {len(quizzes[user_id]['questions'])}"
            )
            context.user_data.clear()
        else:
            quizzes[user_id]["questions"].append(update.message.text)
            await update.message.reply_text(
                f"Question added: {update.message.text}\nUse /add to add more questions or /finish to complete the quiz."
            )

# Main function
def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables.")

    # Start the dummy HTTP server in a separate thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # Start the bot
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create", create_quiz))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
