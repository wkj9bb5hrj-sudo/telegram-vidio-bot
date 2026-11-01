
import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
import yt_dlp

# تحميل التوكن من ملف .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# تفعيل سجل الأخطاء
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def download_and_send_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    # التأكد من أن الرسالة عبارة عن رابط (تبدأ بـ http)
    if not url.startswith("http"):
        await update.message.reply_text("من فضلك أرسل رابط فيديو صحيح (مثل رابط يوتيوب).")
        return

    await update.message.reply_text("⏳ جاري تحميل الفيديو، قد يستغرق ذلك بعض الوقت...")

    # إعدادات تحميل الفيديو باستخدام yt-dlp
    output_template = "downloaded_video.mp4"
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': output_template,
        'max_filesize': 50 * 1024 * 1024, # حد أقصى 50 ميجابايت لرفع تليجرام العادي
    }

    try:
        # تحميل الفيديو
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if os.path.exists(output_template):
            await update.message.reply_text("📤 جاري إرسال الفيديو...")
            with open(output_template, 'rb') as video_file:
                await update.message.reply_video(video=video_file)
            
            # حذف الملف من الجهاز بعد الإرسال لتوفير المساحة
            os.remove(output_template)
        else:
            await update.message.reply_text("❌ حدث خطأ، لم يتم العثور على الفيديو المحمل.")

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"❌ حدث خطأ أثناء التحميل: تأكد من أن الرابط صالح أو أن حجم الفيديو مناسب.")
        if os.path.exists(output_template):
            os.remove(output_template)

def main():
    if not TOKEN:
        print("خطأ: لم يتم العثور على التوكن في ملف .env")
        return

    application = ApplicationBuilder().token(TOKEN).build()

    # معالجة أي رسالة نصية (رابط)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_and_send_video))

    print("بوت تحميل الفيديوهات يعمل الآن وجاهز لاستقبال الروابط...")
    application.run_polling()

if __name__ == "__main__":
    main()