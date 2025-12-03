#!/usr/bin/env python3
"""
Telegram Pakistani SIM Database Bot
A beautiful bot with channel verification and SIM data lookup functionality
"""

import asyncio
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ParseMode

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot Configuration
BOT_TOKEN = "8073948628:AAEeqi-_idwaxQf-bf4qBgFul9h2ju70aAM"
#CHANNEL_USERNAME = "@old_studio786"
#CHANNEL_LINK = "https://t.me/old_studio786"
SIM_API_URL = "https://legendxdata.site/Api/simdata.php?phone="

# User states
user_states = {}

class BotStates:
    WAITING_FOR_CHANNEL_JOIN = "waiting_for_channel_join"
    VERIFIED = "verified"

def validate_pakistani_number(phone_number):
    """Validate if the number is a Pakistani number"""
    clean_number = phone_number.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
    
    # Remove country code prefix if present
    if clean_number.startswith('+92'):
        clean_number = clean_number[3:]
    elif clean_number.startswith('0092'):
        clean_number = clean_number[4:]
    elif clean_number.startswith('92'):
        clean_number = clean_number[2:]
    elif clean_number.startswith('0'):
        clean_number = clean_number[1:]
    
    # Pakistani mobile numbers are 10 digits starting with 3
    if len(clean_number) == 10 and clean_number.startswith('3') and clean_number.isdigit():
        return True, clean_number
    
    return False, None

async def create_loading_animation(message, context: ContextTypes.DEFAULT_TYPE):
    """Create a beautiful loading animation"""
    loading_frames = [
        "🔍 **SEARCHING DATABASE** ⚡",
        "🔍 **SEARCHING DATABASE** ⚡⚡",
        "🔍 **SEARCHING DATABASE** ⚡⚡⚡",
        "📡 **CONNECTING TO SERVER** 🌐",
        "📡 **FETCHING DATA** 📊",
        "⚡ **PROCESSING INFORMATION** 🔄",
        "🔥 **MARA JA RAHA HY SABAR NY HOTY 😅** ✨"
    ]
    
    loading_msg = await message.reply_text(
        loading_frames[0],
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Animate loading
    for frame in loading_frames[1:]:
        await asyncio.sleep(0.8)
        try:
            await loading_msg.edit_text(frame, parse_mode=ParseMode.MARKDOWN)
        except:
            pass  # Ignore rate limit errors
    
    return loading_msg

def format_sim_data(data):
    """Format SIM data response beautifully"""
    if not data or 'error' in data:
        return """
❌ **NO SIM DATA FOUND** ❌

🚫 **SORRY, NO INFORMATION AVAILABLE FOR THIS NUMBER**

💡 **TRY:**
• CHECK THE NUMBER FORMAT 
• ENSURE IT'S A VALID PAKISTANI NUMBER 
• TRY WITHOUT COUNTRY CODE: 3001234567

🔄 **SEND ANOTHER NUMBER TO SEARCHING AGAIN**
        """
    
    # Handle array response from API
    if isinstance(data, list):
        if not data:
            return """
❌ **NO SIM DATA FOUND** ❌

🚫 **SORRY, NO INFORMATION AVAILABLE FOR THIS NUMBER**

💡 **TRY:**
• CHECK THE NUMBER FORMAT 
• ENSURE IT'S A VALID PAKISTANI NUMBER 
• TRY WITHOUT COUNTRY CODE: 3001234567

🔄 **SEND ANOTHER NUMBER TO SEARCH AGAIN**
            """
        
        # Use the first record with most complete data
        record = None
        for item in data:
            if item.get('Name') and item.get('Name').strip():
                record = item
                break
        
        if not record:
            record = data[0]  # Use first record if no complete one found
        
        formatted_text = f"""
🎯 **SIM DATABASE RESULT** 🎯

📱 **NUMBER:** `{record.get('Mobile #', 'N/A')}`
👤 **NAME:** {record.get('Name', 'Not Available')}
🆔 **CNIC:** `{record.get('CNIC', 'N/A')}`
📍 **ADDRESS:** {record.get('Address', 'Not Available')}
📡 **OPERATOR:** {record.get('Operator', 'N/A')}

✅ **YA LO DATA AB POZY MARO LOGO KA MA HACKER HO 😂!**

🔄 **FREE KA MAL HY OUR BE CHECK KAR LO 🤣**

━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 **POWERED BY GABBAR** 🔥
        """
        
        return formatted_text
    
    # Handle single object response
    formatted_text = f"""
🎯 **SIM DATABASE RESULT** 🎯

📱 **NUMBER:** `{data.get('number', data.get('Mobile #', 'N/A'))}`
👤 **NAME:** {data.get('name', data.get('Name', 'Not Available'))}
🆔 **CNIC:** `{data.get('cnic', data.get('CNIC', 'N/A'))}`
📍 **ADDRESS:** {data.get('address', data.get('Address', 'Not Available'))}
📡 **OPERATOR:** {data.get('operator', data.get('Operator', 'N/A'))}

✅ **YA LO DATA AB POZY MARO LOGO KA MA HACKER HO 😂!**

🔄 **FREE KA MAL HY OUR BE CHECK KAR LO 🤣**

━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 **POWERED BY GABBAR** 🔥
    """
    
    return formatted_text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    user_id = update.effective_user.id
    
    welcome_text = """
🔥 **WELCOME TO PAKISTANI SIM DATABASE BOT** 🔥

🚀 **YOU NEED TO JOIN TEAM BLACK HAT OFFICIAL CHANNEL**

⚡ TO ACCESS THE PAKISTANI SIM DATABASE, PLEASE JOIN OUR OFFICIAL CHANNEL FIRST!

🇵🇰 **FEATURES:**
• 📱 PAKISTANI SIM Data LOOKUP
• 🔍 NUMBER INFORMATION (Jazz, Telenor, Ufone, Zong)
• ⚡ FAST & PATA NY KYA 😂
• 🛡️ SECURE DATABASE 

👇 **CLICK THE BUTTON BELLOW TO JOIN:**
    """
    
    keyboard = [
        [InlineKeyboardButton("🚀 JOIN NOW", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ JOINED, VERIFY", callback_data="verify_join")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    user_states[user_id] = BotStates.WAITING_FOR_CHANNEL_JOIN
    
    await update.message.reply_text(
        welcome_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def verify_channel_membership(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Verify if user has joined the channel"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        
        if member.status in ['member', 'administrator', 'creator']:
            user_states[user_id] = BotStates.VERIFIED
            
            success_text = """
✅ **VERIFICATION SUCCESSFUL!** ✅

🎉 WELCOME TO THE PAKISTANI SIM DATABASE BOT!

🇵🇰 **NOW YOU CAN USE THE BOT:**
• SEND ANY PAKISTANI PHONES NUMBER TO GET SIM DATA 
• SUPPORTED NETWORKS: Jazz, Telenor, Ufone, Zong
• FORMAT: +923001234567 or 03001234567

🔥 **ARA NUMBER SEND KAR FAZOOL MA PAR RAHA HY OPER 😂😂!**

💡 **EXAMPLE:** `+923001234567`
            """
            
            await query.edit_message_text(
                success_text,
                parse_mode=ParseMode.MARKDOWN
            )
            
        else:
            error_text = """
❌ **VERIFICATION FAILED!** ❌

🚫 PHALY CHANNEL JOIN KARO PHER ANA 😪!

👇 **PLEASE:**
1️⃣ CLICK "JOIN NOW" BUTTON 
2️⃣ JOIN THE CHANNEL 
3️⃣ COME BACK AND CLICK "JOINED, VERIFY"

⚠️ **YOU MUST JOIN TO USE THIS BOT!**
            """
            
            keyboard = [
                [InlineKeyboardButton("🚀 JOIN NOW", url=CHANNEL_LINK)],
                [InlineKeyboardButton("✅ JOINED, VERIFY", callback_data="verify_join")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                error_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
    except Exception as e:
        logger.error(f"Error checking membership: {e}")
        await query.edit_message_text(
            "❌ **Error verifying membership. Please try again later.**",
            parse_mode=ParseMode.MARKDOWN
        )

async def handle_number_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle phone number input and fetch SIM data"""
    user_id = update.effective_user.id
    
    # Check if user is verified
    if user_states.get(user_id) != BotStates.VERIFIED:
        keyboard = [
            [InlineKeyboardButton("🚀 JOIN NOW", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ JOINED, VERIFY", callback_data="verify_join")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🚫 **KAL ANA HA KAL 😂😂!**",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        return
    
    phone_number = update.message.text.strip()
    
    # Validate Pakistani phone number
    is_valid, clean_number = validate_pakistani_number(phone_number)
    
    if not is_valid:
        await update.message.reply_text(
            """
❌ **INVALID PAKISTANI NUMBER** ❌

🇵🇰 **THIS BOT ONLY WORK'S WITH PAKISTANI NUMBERS!**

📱 **ACCEPTED FORMATS:**
• `+923001234567`
• `923001234567`
• `03001234567`
• `3001234567`

💡 **EXAMPLES:**
• `+923001234567` (Jazz/Warid)
• `+923451234567` (Telenor)
• `+923331234567` (Ufone)
• `+923551234567` (Zong)

🚫 **NOTE:** ONLY PAKISTANI MOBILE NUMBERS ARE SUPPORTED!
            """,
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Show loading animation
    loading_msg = await create_loading_animation(update.message, context)
    
    try:
        # Make API request with Pakistani number format (without country code)
        response = requests.get(f"{SIM_API_URL}{clean_number}", timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
            except:
                data = {"number": clean_number, "info": response.text}
        else:
            data = {"error": f"API returned status code {response.status_code}"}
            
    except requests.exceptions.Timeout:
        data = {"error": "Request timeout"}
    except requests.exceptions.RequestException as e:
        data = {"error": f"Network error: {str(e)}"}
    except Exception as e:
        data = {"error": f"Unexpected error: {str(e)}"}
    
    # Format and send result
    result_text = format_sim_data(data)
    
    try:
        await loading_msg.edit_text(result_text, parse_mode=ParseMode.MARKDOWN)
    except:
        await loading_msg.delete()
        await update.message.reply_text(result_text, parse_mode=ParseMode.MARKDOWN)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_text = """
🔥 **PAKISTANI SIM DATABASE BOT HELP** 🔥

🇵🇰 **HOW TO USE:**
1️⃣ JOIN OUR OFFICIAL CHANNEL 
2️⃣ GET VERIFIED 
3️⃣ SEND ANY PAKISTANI PHONES NUMBER 
4️⃣ GET SIM DATA INSTANTLY!

🎯 **COMMANDS:**
• `/start` - START THE BOT 
• `/help` - SHOW THIS HELP MESSAGE 

💡 **PAKISTANI NUMBER FORMATS SUPPORTED:**
• `+923001234567`
• `923001234567`
• `03001234567`
• `3001234567`

📡 **SUPPORTED NETWORKS:**
• Jazz/Warid (300, 301, 302, 303, 304, 305)
• Telenor (345, 346, 347, 348, 349)
• Ufone (333, 334, 335, 336, 337)
• Zong (355, 356, 357, 358, 359)

🔗 **CHANNEL:** {CHANNEL_LINK}

🛡️ **SECURE • FAST • RELIABLE**
    """
    
    await update.message.reply_text(
        help_text.format(CHANNEL_LINK=CHANNEL_LINK),
        parse_mode=ParseMode.MARKDOWN
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors"""
    logger.error(f"Exception while handling an update: {context.error}")

def main() -> None:
    """Start the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(verify_channel_membership, pattern="verify_join"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_number_input))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    print("🚀 PAKISTANI SIM DATABASE BOT IS STARTING...")
    print("🔥 BOT IS RUNNING! PRESS Ctrl+C TO STOP.")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

