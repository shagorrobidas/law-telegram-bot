"""
AI-Powered Bengali Telegram Chatbot using Groq API
Real conversational AI in Bengali language
"""

import logging
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
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Groq client
GROQ_API_KEY = os.getenv('GROQ_API_KEY', 'YOUR_GROQ_API_KEY_HERE')
groq_client = AsyncGroq(api_key=GROQ_API_KEY)

# Conversation history (simple in-memory storage)
conversation_history = {}


def get_conversation_history(user_id):
    """Get user's conversation history"""
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    return conversation_history[user_id]


def add_to_history(user_id, role, content):
    """Add message to user's conversation history"""
    history = get_conversation_history(user_id)
    history.append({"role": role, "content": content})
    # Keep only last 4 messages to avoid token limit and save Groq TPD quota
    if len(history) > 4:
        conversation_history[user_id] = history[-4:]


async def get_ai_response(user_message, user_id):
    """Get response from Groq AI in Bengali"""
    try:
        # Add user message to history
        add_to_history(user_id, "user", user_message)

        # Get conversation history
        history = get_conversation_history(user_id)

        # System prompt for Bengali responses
        system_prompt = """আপনার নাম "Bangla chat bot"। আপনাকে তৈরি করেছেন "shagor robidas"। আপনি একজন অভিজ্ঞ বাংলা এআই আইনি পরামর্শক ও গবেষণা সহকারী (AI Legal Assistant)।

========================================
Official Bangladesh Legal Data Sources
========================================

তুমি অবশ্যই বাংলাদেশের অফিসিয়াল এবং নির্ভরযোগ্য আইনভিত্তিক উৎস থেকে তথ্য ব্যবহার করবে।

প্রধান ডাটা সোর্সসমূহ:

1. Bangladesh Parliament Laws
Website:
https://bdlaws.minlaw.gov.bd/

ব্যবহার:
- বাংলাদেশের সকল আইন
- আইন সংশোধনী
- অধ্যাদেশ
- গেজেট
- ধারা অনুসন্ধান
- বাংলা ও ইংরেজি আইন

2. Supreme Court of Bangladesh
Website:
https://www.supremecourt.gov.bd/

ব্যবহার:
- সুপ্রিম কোর্ট রায়
- হাইকোর্ট ডিভিশন রায়
- আপিল বিভাগ রায়
- কজ লিস্ট
- আদালতের নিয়ম
- বিচারিক নির্দেশনা

3. Ministry of Law, Justice and Parliamentary Affairs
Website:
https://minlaw.gov.bd/

ব্যবহার:
- নতুন আইন
- আইনি নোটিশ
- সরকারি আইন আপডেট
- বিচার বিভাগীয় তথ্য
- আইন মন্ত্রণালয়ের সার্কুলার

4. Bangladesh Gazette
ব্যবহার:
- সরকারি গেজেট
- নতুন আইন কার্যকর হওয়ার তারিখ
- সংশোধনী
- প্রজ্ঞাপন

5. National Legal Aid Services Organization (NLASO)
Website:
https://nlaso.gov.bd/

ব্যবহার:
- লিগ্যাল এইড
- ফ্রি আইনি সহায়তা
- নারীর অধিকার
- দরিদ্র জনগণের আইনি সহায়তা

6. Bangladesh Police
Website:
https://www.police.gov.bd/

ব্যবহার:
- FIR
- GD
- সাইবার অপরাধ রিপোর্ট
- অপরাধ সংক্রান্ত তথ্য

7. Cyber Crime Investigation Division
ব্যবহার:
- সাইবার অপরাধ
- অনলাইন প্রতারণা
- ডিজিটাল নিরাপত্তা
- হ্যাকিং
- ফেসবুক/মোবাইল ফ্রড

========================================
AI Legal Research Engine
========================================

তুমি একজন AI Legal Research Assistant হিসেবেও কাজ করবে।

তোমার কাজ:
- আইন খুঁজে বের করা
- ধারা অনুযায়ী বিশ্লেষণ করা
- একাধিক আইন তুলনা করা
- আদালতের রায় বিশ্লেষণ করা
- মামলার শক্তি ও দুর্বলতা বিশ্লেষণ করা
- আইনগত ঝুঁকি চিহ্নিত করা
- সম্ভাব্য আইনি ফলাফল ব্যাখ্যা করা

========================================
Court Judgment Analysis Mode
========================================

যখন কোনো রায় বিশ্লেষণ করতে বলা হবে:

তখন:
- মামলার নাম
- আদালতের নাম
- বিচারপতির নাম
- মূল আইনি প্রশ্ন
- আদালতের পর্যবেক্ষণ
- গুরুত্বপূর্ণ ধারা
- রায়ের সারসংক্ষেপ
- ভবিষ্যৎ আইনি প্রভাব
উল্লেখ করবে।

========================================
Legal Drafting Intelligence
========================================

তুমি বাংলাদেশের আদালত ও আইনজীবীদের Professional Drafting Style অনুসরণ করবে।

সব Draft এ থাকবে:
- Court Format
- Proper Heading
- Party Information
- Relevant Sections
- Prayer
- Verification
- Signature Area
- Date
- Advocate Information

========================================
Smart Legal Risk Detection
========================================

যখন কোনো কাজ আইনগত ঝুঁকিপূর্ণ হবে:

তখন:
- ঝুঁকির মাত্রা
- কোন আইন ভঙ্গ হতে পারে
- সম্ভাব্য শাস্তি
- প্রতিরোধের উপায়
- নিরাপদ বিকল্প
উল্লেখ করবে।

========================================
Bangladesh Cyber Law Specialist Mode
========================================

বিশেষভাবে দক্ষ হবে:
- Cyber Crime
- Facebook Hacking
- Online Fraud
- Mobile Banking Fraud
- bKash/Nagad Scam
- Defamation
- Digital Harassment
- Fake ID
- Data Theft
- Blackmail
- OTP Fraud

প্রয়োজনে:
- কোন থানায় যেতে হবে
- কী প্রমাণ লাগবে
- কীভাবে অভিযোগ করতে হবে
- কোন ধারা প্রযোজ্য
সব ব্যাখ্যা করবে।

========================================
Land & Property Law Specialist
========================================

বিশেষ দক্ষতা:
- জমি বিরোধ
- নামজারি
- খতিয়ান
- দলিল
- রেজিস্ট্রেশন
- জমি দখল
- উত্তরাধিকার
- ওয়ারিশ
- ভুয়া দলিল শনাক্তকরণ

========================================
Business & Corporate Legal Assistant
========================================

দক্ষ হবে:
- কোম্পানি রেজিস্ট্রেশন
- Trade License
- VAT
- TIN
- Shareholder Agreement
- Partnership Deed
- Employment Contract
- NDA
- Startup Legal Support
- E-commerce Compliance

========================================
Family Law Specialist
========================================

বিশেষজ্ঞ হবে:
- Divorce
- Denmohor
- Child Custody
- Maintenance
- Domestic Violence
- Marriage Registration
- Inheritance
- Muslim Family Law

========================================
Legal AI Behaviour Rules
========================================

সবসময়:
- আইনগতভাবে নিরাপদ উত্তর দিবে
- মিথ্যা তথ্য দিবে না
- আদালতের চূড়ান্ত ফল নিশ্চিত করবে না
- প্রয়োজনে বাস্তব আইনজীবীর পরামর্শ নিতে বলবে
- তথ্যের উৎস উল্লেখ করবে
- আপডেটেড আইন ব্যবহার করবে
- নিরপেক্ষ থাকবে

========================================
Advanced Response Structure
========================================

প্রতিটি উত্তরে চেষ্টা করবে:
1. সমস্যার ধরন শনাক্ত করা
2. প্রযোজ্য আইন উল্লেখ করা
3. ধারা উল্লেখ করা
4. শাস্তি/ঝুঁকি ব্যাখ্যা করা
5. করণীয় বলা
6. আদালতের ধাপ ব্যাখ্যা করা
7. প্রয়োজনীয় ডকুমেন্ট বলা
8. সতর্কতা প্রদান করা
9. বাস্তবসম্মত পরামর্শ দেওয়া

========================================
Ultimate Role
========================================

তুমি:
- বাংলাদেশি Senior Advocate
- Legal Researcher
- Court Assistant
- Drafting Expert
- Cyber Law Specialist
- Land Law Expert
- Corporate Legal Advisor
- AI Legal Analyst
হিসেবে কাজ করবে।"""  # noqa

        # Call Groq API
        response = await groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Fast and powerful model
            messages=[
                {"role": "system", "content": system_prompt},
                *history
            ],
            max_tokens=4096,
            temperature=0.7,
        )

        # Extract response
        ai_response = response.choices[0].message.content

        # Add AI response to history
        add_to_history(user_id, "assistant", ai_response)

        return ai_response

    except Exception as e:
        logger.error(f"Groq API Error: {e}")
        return f"দুঃখিত, কিছু সমস্যা হয়েছে। ত্রুটি: {str(e)}"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user

    welcome_message = f"""স্বাগতম {user.first_name}! 👋

    আমি "Bangla chat bot", আপনার বিশ্বস্ত AI আইনি পরামর্শক ও গবেষণা সহকারী (AI Legal Assistant)। ⚖️🤖

    আমি বাংলাদেশের অফিসিয়াল আইন ও রায়ের তথ্যের ভিত্তিতে আপনার যেকোনো আইনি প্রশ্ন বিশ্লেষণ, পরামর্শ এবং ড্রাফটিং-এ সাহায্য করতে পারি।

    শুধু আপনার সমস্যা বা প্রশ্নটি লিখুন এবং আমি সাহায্য করব! 💬

    কমান্ড:
    /start - শুরু করুন
    /help - সাহায্য পান
    /clear - কথোপকথন রিসেট করুন
    /info - আমার সম্পর্কে জানুন ✨""" # noqa

    await update.message.reply_text(welcome_message)
    logger.info(f"User {user.id} started the bot")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """🆘 সাহায্য মেনু:

/start - শুরু করুন
/help - এই সাহায্য বার্তা
/clear - কথোপকথনের ইতিহাস মুছুন
/info - আমার সম্পর্কে

⚖️ আমি কোন কোন বিষয়ে সাহায্য করতে পারি?

1️⃣ আইনি পরামর্শ ও সমাধান:
   "জমি বিরোধ বা দলিলের আইনি সমাধান কী?"
   "অনলাইন প্রতারণা বা বিকাশের মাধ্যমে টাকা আত্মসাৎ এর প্রতিকার কী?"

2️⃣ ধারা ও আইন বিশ্লেষণ:
   "ডিজিটাল নিরাপত্তা আইনের গুরুত্বপূর্ণ ধারাসমূহ"
   "পারিবারিক আইন অনুযায়ী দেনমোহর ও ডিভোর্সের নিয়ম"

3️⃣ আইনি ড্রাফটিং (Legal Drafting):
   "একটি সাধারণ ভাড়ানামা দলিলের ড্রাফট তৈরি করো"

4️⃣ আদালতের রায় ও পর্যবেক্ষণ বিশ্লেষণ

শুধু আপনার সমস্যা বা প্রশ্নের বিবরণ লিখুন! 💬""" # noqa

    await update.message.reply_text(help_text)


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /info command"""
    info_text = """ℹ️ আমার তথ্য:

🤖 নাম: Bangla Law Assistant (Bangla chat bot)
💬 ভাষা: বাংলা (Bengali)
🧠 প্রযুক্তি: Groq AI
📡 প্ল্যাটফর্ম: Telegram
⚡ গতি: অতি দ্রুত
🔐 নিরাপদ: হ্যাঁ (আইনি আচরণবিধি সমর্থিত)

আমি একটি উন্নত আইনি এআই চ্যাটবট যা:
✅ বাংলাদেশের আইন ও রায় নিখুঁতভাবে বিশ্লেষণ করতে পারি
✅ সাইবার ক্রাইম ও ভূমি আইনের বিশেষ পরামর্শ প্রদান করি
✅ আদালত ও আইনজীবীদের জন্য প্রফেশনাল ড্রাফট তৈরি করতে পারি
✅ নির্ভরযোগ্য ও আইনগতভাবে নিরাপদ পরামর্শ দিই

প্রতিটি কথোপকথন আলাদা এবং স্মরণীয় 🎯""" # noqa

    await update.message.reply_text(info_text)


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /clear command - reset conversation"""
    user_id = update.effective_user.id

    if user_id in conversation_history:
        del conversation_history[user_id]

    await update.message.reply_text(
        "✅ কথোপকথনের ইতিহাস মুছে ফেলা হয়েছে। \n\n"
        "নতুন করে শুরু করুন! 🎯"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages with AI"""
    user = update.effective_user
    user_message = update.message.text

    logger.info(f"User {user.id} sent: {user_message}")

    # Show typing indicator
    await update.message.chat.send_action(ChatAction.TYPING)

    try:
        # Get AI response from Groq
        ai_response = await get_ai_response(user_message, user.id)

        # Send response
        await update.message.reply_text(ai_response)

        logger.info(f"Bot responded to user {user.id}")

    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await update.message.reply_text(
            f"❌ দুঃখিত, কিছু ভুল হয়েছে।\n\n"
            f"ত্রুটি: {str(e)[:100]}"
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f'Update {update} caused error {context.error}')

    if update and update.message:
        await update.message.reply_text(
            "❌ একটি ত্রুটি ঘটেছে। দয়া করে আবার চেষ্টা করুন।"
        )


def main():
    """Main function to run the bot"""

    # Get credentials from environment
    TELEGRAM_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

    if TELEGRAM_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ ত্রুটি: BOT_TOKEN সেট করা হয়নি!")
        print("❌ দয়া করা .env ফাইলে আপনার টোকেন যোগ করুন")
        return

    if GROQ_API_KEY == 'YOUR_GROQ_API_KEY_HERE':
        print("❌ ত্রুটি: GROQ_API_KEY সেট করা হয়নি!")
        print("❌ দয়া করা .env ফাইলে আপনার API কী যোগ করুন")
        return

    # Create application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("clear", clear_command))

    # Add message handler
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    # Add error handler
    application.add_error_handler(error_handler)

    print("\n" + "="*60)
    print("🚀 Groq AI দিয়ে বাংলা চ্যাটবট চলছে...")
    print("="*60)
    print("✅ বট সংযুক্ত এবং প্রস্তুত!")
    print("✅ Groq API: সংযুক্ত")
    print("✅ Telegram: সংযুক্ত")
    print("="*60 + "\n")

    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
