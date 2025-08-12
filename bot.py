from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
import os
import asyncio
import nest_asyncio  # ← برای رفع محدودیت حلقه‌ی asyncio در محیط‌های خاص

nest_asyncio.apply()  # ← فعال‌سازی اجرای همزمان حلقه

# 🔐 شناسه عددی مدیر
ADMIN_ID = 7399153044  # ← شناسه عددی تلگرام خودتان

# 🔑 توکن ربات
TOKEN = os.environ["BOT_TOKEN"]

# 📁 مسیر ذخیره‌سازی فیلم‌ها
VIDEO_DIR = "videos"
os.makedirs(VIDEO_DIR, exist_ok=True)

# 🗂 لیست فیلم‌ها
video_files = []

# 🎬 دستور /start
async def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("📥 ذخیره فیلم", callback_data='save')],
            [InlineKeyboardButton("🗑 حذف فیلم", callback_data='delete')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🎉 خوش آمدید مدیر عزیز!\nلطفاً انتخاب کنید:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("👋 خوش آمدید!\nبرای دیدن فیلم‌ها از دستور /videos استفاده کنید.")

# 📥 دریافت فیلم از مدیر
async def handle_video(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ فقط مدیر می‌تواند فیلم ذخیره کند.")
        return

    video = update.message.video
    file = await context.bot.get_file(video.file_id)
    filename = f"{VIDEO_DIR}/{video.file_unique_id}.mp4"
    await file.download_to_drive(filename)
    video_files.append(filename)
    await update.message.reply_text("✅ فیلم با موفقیت ذخیره شد.")

# 📤 نمایش فیلم‌ها به کاربران
async def show_videos(update: Update, context: CallbackContext):
    if not video_files:
        await update.message.reply_text("هیچ فیلمی ذخیره نشده است.")
        return

    for path in video_files:
        with open(path, 'rb') as f:
            await update.message.reply_video(video=f)

# 🗑 حذف فیلم‌ها توسط مدیر
async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.edit_message_text("⛔ فقط مدیر می‌تواند این عملیات را انجام دهد.")
        return

    if query.data == 'save':
        await query.edit_message_text("لطفاً فیلم را ارسال کنید تا ذخیره شود.")
    elif query.data == 'delete':
        if not video_files:
            await query.edit_message_text("هیچ فیلمی برای حذف وجود ندارد.")
            return
        last_video = video_files.pop()
        os.remove(last_video)
        await query.edit_message_text("🗑 آخرین فیلم حذف شد.")

# 🚀 راه‌اندازی ربات
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("videos", show_videos))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 ربات فعال شد...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())