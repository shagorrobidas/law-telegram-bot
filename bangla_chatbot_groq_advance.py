"""
Advanced Bengali Telegram Chatbot with Groq AI
Features: Persistent memory, user tracking, context awareness, streaming
"""

import logging
import json
import os
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from telegram.constants import ChatAction
from groq import AsyncGroq
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Groq
GROQ_API_KEY = os.getenv('GROQ_API_KEY', 'YOUR_GROQ_API_KEY_HERE')
groq_client = AsyncGroq(api_key=GROQ_API_KEY)

# Database configuration
DATABASE_FILE = "chatbot_database.json"


class ChatbotDatabase:
    """Persistent database for user data and conversations"""

    def __init__(self, filename=DATABASE_FILE):
        self.filename = filename
        self.load()

    def load(self):
        """Load database from file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except Exception as e:
                logger.error(f"Database load error: {e}")
                self.data = {}
        else:
            self.data = {}

    def save(self):
        """Save database to file"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Database save error: {e}")

    def create_user(self, user_id, username, first_name):
        """Create new user profile"""
        user_id_str = str(user_id)
        if user_id_str not in self.data:
            self.data[user_id_str] = {
                'username': username,
                'first_name': first_name,
                'created_at': datetime.now().isoformat(),
                'messages_count': 0,
                'conversations': {},
                'preferences': {
                    'language': 'bengali',
                    'tone': 'friendly',
                    'max_history': 15
                }
            }
            self.save()

    def add_message(self, user_id, message, response):
        """Add message to conversation history"""
        user_id_str = str(user_id)
        if user_id_str in self.data:
            user = self.data[user_id_str]
            user['messages_count'] += 1

            # Create conversation session
            session_date = datetime.now().strftime('%Y-%m-%d')
            if session_date not in user['conversations']:
                user['conversations'][session_date] = []

            # Add to conversation
            user['conversations'][session_date].append({
                'timestamp': datetime.now().isoformat(),
                'user_message': message,
                'bot_response': response
            })

            # Keep only last N conversations per day
            max_history = user['preferences'].get('max_history', 15)
            if len(user['conversations'][session_date]) > max_history:
                user['conversations'][session_date] = \
                    user['conversations'][session_date][-max_history:]

            self.save()

    def get_user_history(self, user_id, limit=10):
        """Get user's recent conversation history"""
        user_id_str = str(user_id)
        if user_id_str not in self.data:
            return []

        user = self.data[user_id_str]
        history = []

        # Get messages from all sessions
        for session_key in sorted(user['conversations'].keys(), reverse=True):
            messages = user['conversations'][session_key]
            history.extend(messages)
            if len(history) >= limit:
                break

        return history[-limit:]

    def get_user_stats(self, user_id):
        """Get user statistics"""
        user_id_str = str(user_id)
        if user_id_str not in self.data:
            return None

        user = self.data[user_id_str]
        total_sessions = len(user['conversations'])

        return {
            'username': user.get('username'),
            'first_name': user.get('first_name'),
            'messages_count': user['messages_count'],
            'total_sessions': total_sessions,
            'created_at': user['created_at'],
            'last_active': user['preferences'].get('last_active')
        }

    def clear_user_data(self, user_id):
        """Clear user's conversation data"""
        user_id_str = str(user_id)
        if user_id_str in self.data:
            self.data[user_id_str]['conversations'] = {}
            self.data[user_id_str]['messages_count'] = 0
            self.save()


# Initialize database
db = ChatbotDatabase()


def build_prompt_with_context(user_message, user_id):
    """Build AI prompt with user history context"""

    # Get recent history
    history = db.get_user_history(user_id, limit=5)

    context = ""
    if history:
        context = "\n\nব্যবহারকারীর সাম্প্রতিক প্রশ্ন ও উত্তর:\n"
        for item in history[-3:]:  # Last 3 messages for context
            context += f"ব্যবহারকারী: {item['user_message']}\n"
            context += f"সহায়ক: {item['bot_response'][:100]}...\n\n"

    system_prompt = f"""
        আপনার নাম "Bangla chat bot"। আপনাকে তৈরি করেছেন "sagor robidas"।
        আপনি একজন অভিজ্ঞ বাংলা ভার্চুয়াল সহায়ক।

        আপনার বৈশিষ্ট্য:
        ✓ সর্বদা বাংলায় উত্তর দিন
        ✓ স্বাভাবিক এবং বন্ধুত্বপূর্ণ টোন বজায় রাখুন
        ✓ প্রসঙ্গ (context) বুঝুন এবং ব্যবহার করুন
        ✓ দীর্ঘ এবং বিস্তৃত উত্তর দিন (১-২ অনুচ্ছেদ)
        ✓ প্রয়োজনে মোজি ব্যবহার করুন
        ✓ যদি জানেন না তবে সৎভাবে বলুন

        আপনি করতে পারেন:
        • তথ্য এবং পরামর্শ প্রদান
        • গল্প এবং কবিতা লেখা
        • সমস্যা সমাধানে সাহায্য করা
        • জটিল বিষয় সহজভাবে ব্যাখ্যা করা
        • সৃজনশীল কাজে সহায়তা করা

        {context}

        এই প্রসঙ্গ মাথায় রেখে ব্যবহারকারীর নতুন প্রশ্নের উত্তর দিন।
    """

    return system_prompt


async def get_ai_response(user_message, user_id):
    """Get AI response from Groq with context"""
    try:
        # Build prompt with context
        system_prompt = build_prompt_with_context(user_message, user_id)

        # Call Groq API
        response = await groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=4096,
            temperature=0.8,
        )

        ai_response = response.choices[0].message.content

        # Save to database
        db.add_message(user_id, user_message, ai_response)

        return ai_response

    except Exception as e:
        logger.error(f"Groq Error: {e}")
        return f"দুঃখিত, AI সেবা এখন উপলব্ধ নয়। ত্রুটি: {str(e)[:50]}"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    user = update.effective_user
    db.create_user(user.id, user.username, user.first_name)

    welcome = f"""🎉 স্বাগতম {user.first_name}!

আমি "Bangla chat bot"। আমাকে তৈরি করেছেন "shagor robidas"। 🤖

আমি আপনার সাথে প্রতিটি কথোপকথন মনে রাখি এবং
প্রসঙ্গ (context) সহ ভালো উত্তর দিতে পারি।

🚀 আমি করতে পারি:
  • যেকোনো প্রশ্নের উত্তর দেওয়া
  • গল্প, কবিতা লেখা
  • পরামর্শ দেওয়া
  • জটিল বিষয় সহজ করা
  • সৃজনশীল কাজে সাহায্য করা

📋 কমান্ড:
  /start - শুরু করুন
  /help - সাহায্য পান
  /stats - আপনার পরিসংখ্যান
  /clear - কথোপকথন মুছুন
  /info - আমার সম্পর্কে

শুধু কিছু লিখুন শুরু করতে! 💬"""

    await update.message.reply_text(welcome)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = """
        🆘 আপনি কী জানতে চান?

        📚 কমান্ড:
        /start - শুরু করুন
        /help - এই সাহায্য বার্তা
        /stats - আপনার ব্যবহার পরিসংখ্যান
        /clear - সব কথোপকথন মুছুন
        /info - বটের তথ্য

        💡 ব্যবহারের টিপস:
        ✓ যেকোনো প্রশ্ন করুন
        ✓ আমি প্রসঙ্গ মনে রাখি
        ✓ প্রতিদিন নতুন সেশন শুরু হয়
        ✓ আগের কথোপকথন ব্যবহার করি

        🎯 উদাহরণ:
        "আমাকে একটি মজার গল্প বলো"
        "বাংলাদেশের রাজধানী কোথায়?"
        "পরিবেশ রক্ষায় আমি কী করতে পারি?"
        "একটি বাংলা কবিতা লিখো"

        যেকোনো সময় লিখুন! 💬
    """

    await update.message.reply_text(help_text)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user statistics"""
    user = update.effective_user
    stats = db.get_user_stats(user.id)

    if stats:
        stats_text = f"""📊 আপনার পরিসংখ্যান:

👤 নাম: {stats['first_name']}
💬 মোট বার্তা: {stats['messages_count']}
📅 মোট সেশন: {stats['total_sessions']}
🗓️ যোগদান: {stats['created_at'][:10]}

আপনি আমার একজন অনুগত ব্যবহারকারী! 🌟"""
    else:
        stats_text = "আপনার কোনো ডেটা নেই। /start দিয়ে শুরু করুন।"

    await update.message.reply_text(stats_text)


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear conversation"""
    db.clear_user_data(update.effective_user.id)
    await update.message.reply_text(
        "✅ আপনার সব কথোপকথন মুছে ফেলা হয়েছে।\n"
        "নতুন করে শুরু করুন! 🎯"
    )


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot information"""
    info = """
        ℹ️ বটের তথ্য:

        🤖 নাম: Bangla chat bot
        ✍️ নির্মাতা: shagor robidas
        💬 ভাষা: বাংলা (Bengali)
        🧠 প্রযুক্তি: Groq AI (Llama 3.3 70B)
        📡 প্ল্যাটফর্ম: Telegram
        ⚡ গতি: অতি দ্রুত
        💾 স্মৃতি: স্থায়ী (Persistent)

        🎯 বৈশিষ্ট্য:
        ✅ প্রসঙ্গ-সচেতন উত্তর
        ✅ কথোপকথন ইতিহাস
        ✅ ব্যবহারকারী পরিসংখ্যান
        ✅ উন্নত AI ক্ষমতা
        ✅ বাংলা সম্পূর্ণ সমর্থন

        🔒 আপনার ডেটা নিরাপদ এবং গোপনীয়।
    """

    await update.message.reply_text(info)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages"""
    user = update.effective_user
    message = update.message.text

    logger.info(f"User {user.id}: {message}")

    # Ensure user exists
    db.create_user(user.id, user.username, user.first_name)

    # Show typing
    await update.message.chat.send_action(ChatAction.TYPING)

    try:
        # Get AI response
        response = await get_ai_response(message, user.id)

        # Split long messages
        if len(response) > 4096:
            for i in range(0, len(response), 4096):
                await update.message.reply_text(response[i:i+4096])
        else:
            await update.message.reply_text(response)

        logger.info(f"Responded to user {user.id}")

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(
            f"❌ দুঃখিত, একটি ত্রুটি ঘটেছে।\n\n"
            f"বিবরণ: {str(e)[:100]}"
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Error handler"""
    logger.error(f'Error: {context.error}')


def main():
    """Main function"""
    TELEGRAM_TOKEN = os.getenv(
        'BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE'
    )

    # Validation
    if TELEGRAM_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ BOT_TOKEN সেট করা হয়নি!")
        return

    if GROQ_API_KEY == 'YOUR_GROQ_API_KEY_HERE':
        print("❌ GROQ_API_KEY সেট করা হয়নি!")
        return

    # Setup application
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )
    app.add_error_handler(error_handler)

    print("\n" + "="*70)
    print("🚀 Bangla chat bot (created by shagor robidas) চলছে...")
    print("="*70)
    print("✅ Groq AI: সংযুক্ত")
    print("✅ Telegram: সংযুক্ত")
    print("✅ ডাটাবেস: সংযুক্ত")
    print("="*70)
    print("\n🎯 এখন আপনার বট প্রস্তুত!")
    print("="*70 + "\n")

    # Start polling
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()