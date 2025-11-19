import os
import requests
import random
import json
import time
import logging
from telegram.ext import Application, CommandHandler
import asyncio

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# التوكن
BOT_TOKEN = os.getenv('BOT_TOKEN', '8198990470:AAHjcpxW0oCXZZq4RL6pCN2II292iETc7Hc')

print(f"🔧 بدء تشغيل البوت...")
print(f"📝 طول التوكن: {len(BOT_TOKEN)}")

class TikTokChecker:
    def __init__(self):
        self.checked_count = 0
        print("✅ TikTokChecker جاهز")
        
    def check_username(self, username):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            url = f"https://www.tiktok.com/@{username}"
            response = requests.get(url, headers=headers, timeout=10)
            self.checked_count += 1
            
            if response.status_code == 404:
                logger.info(f"✅ متاح: @{username}")
                return True
            return False
        except Exception as e:
            logger.error(f"خطأ في فحص {username}: {e}")
            return False
    
    def load_saved(self):
        try:
            if os.path.exists("saved.json"):
                with open("saved.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"خطأ في تحميل المحفوظات: {e}")
            return []
    
    def save_username(self, username):
        try:
            saved = self.load_saved()
            if username not in saved:
                saved.append(username)
                with open("saved.json", "w", encoding="utf-8") as f:
                    json.dump(saved, f, ensure_ascii=False, indent=2)
                logger.info(f"💾 تم حفظ: @{username}")
                return True
            return False
        except Exception as e:
            logger.error(f"خطأ في الحفظ: {e}")
            return False
    
    def generate_usernames(self, count=5):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
        return [''.join(random.choices(chars, k=3)) for _ in range(count)]

checker = TikTokChecker()

async def start(update, context):
    await update.message.reply_text(
        "🎯 بوت يوزرات تيك توك النادرة!\n\n"
        "🔍 الأوامر:\n"
        "/quick - بحث سريع\n"
        "/saved - المحفوظات\n"
        "/stats - الإحصائيات\n\n"
        "⚡ البوت يعمل على السيرفر!"
    )

async def quick_search(update, context):
    await update.message.reply_text("🔍 جاري البحث السريع...")
    
    try:
        usernames = checker.generate_usernames(5)
        available = []
        saved_count = 0
        
        for username in usernames:
            if checker.check_username(username):
                available.append(username)
                if checker.save_username(username):
                    saved_count += 1
            time.sleep(1)  # تأخير بين الطلبات
        
        if available:
            msg = "✅ **اليوزرات المتاحة:**\n\n"
            for u in available:
                msg += f"• `@{u}`\n"
            msg += f"\n💾 تم حفظ {saved_count} يوزر"
        else:
            msg = "❌ لم أعثر على يوزرات متاحة في هذه الجولة"
            
        await update.message.reply_text(msg)
        
    except Exception as e:
        logger.error(f"خطأ في البحث: {e}")
        await update.message.reply_text("❌ حدث خطأ أثناء البحث")

async def saved(update, context):
    try:
        saved = checker.load_saved()
        if saved:
            msg = "💾 **اليوزرات المحفوظة:**\n\n"
            for i, u in enumerate(saved[:10], 1):
                msg += f"{i}. `@{u}`\n"
            msg += f"\n📊 المجموع: {len(saved)} يوزر"
        else:
            msg = "💾 لا توجد يوزرات محفوظة"
        
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text("❌ خطأ في تحميل المحفوظات")

async def stats(update, context):
    saved_count = len(checker.load_saved())
    msg = f"""📊 **إحصائيات البوت**

💾 اليوزرات المحفوظة: {saved_count}
⚡ اليوزرات المفحوصة: {checker.checked_count}

🚀 البوت شغال بشكل مستمر!"""
    
    await update.message.reply_text(msg)

def main():
    try:
        print("🚀 بدء تشغيل البوت...")
        
        # إنشاء التطبيق
        application = Application.builder().token(BOT_TOKEN).build()
        
        # إضافة الأوامر
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("quick", quick_search))
        application.add_handler(CommandHandler("saved", saved))
        application.add_handler(CommandHandler("stats", stats))
        
        print("✅ البوت جاهز للتشغيل!")
        print("🤖 إرسل /start للبوت للتجربة")
        
        # تشغيل البوت
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ فشل في تشغيل البوت: {e}")
        print(f"❌ الخطأ: {e}")

if __name__ == '__main__':
    main()
