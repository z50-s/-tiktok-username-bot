import os
import requests
import random
import json
import time
import logging
import threading
import asyncio
from telegram.ext import Application, CommandHandler, ContextTypes

# إعداد تسجيل مبسط
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# التوكن - مع قيمة افتراضية آمنة
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8198990470:AAHjcpxW0oCXZZq4RL6pCN2II292iETc7Hc')

print("=" * 50)
print("🤖 بوت يوزرات تيك توك - الإصدار المبسط")
print("✅ متوافق مع Koyeb")
print("=" * 50)

class SimpleTikTokBot:
    def __init__(self):
        self.checked_count = 0
        self.found_count = 0
        self.is_running = False
        self.thread = None
        
    def check_username(self, username):
        """فحص بسيط لليوزر"""
        try:
            url = f"https://www.tiktok.com/@{username}"
            response = requests.get(url, timeout=10)
            self.checked_count += 1
            
            if response.status_code == 404:
                return True
            return False
        except:
            return False
    
    def load_saved(self):
        """تحميل المحفوظات"""
        try:
            if os.path.exists("data.json"):
                with open("data.json", "r") as f:
                    return json.load(f)
            return []
        except:
            return []
    
    def save_username(self, username):
        """حفظ اليوزر"""
        try:
            saved = self.load_saved()
            if username not in saved:
                saved.append(username)
                with open("data.json", "w") as f:
                    json.dump(saved, f)
                return True
            return False
        except:
            return False
    
    def generate_usernames(self, count=10):
        """توليد يوزرات"""
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
        usernames = []
        
        for _ in range(count):
            length = random.choice([3, 4])
            username = ''.join(random.choices(chars, k=length))
            usernames.append(username)
        
        return usernames
    
    def start_auto_search(self, bot_instance, chat_id):
        """بدء البحث التلقائي"""
        if self.is_running:
            return False
            
        self.is_running = True
        
        def search_loop():
            round_num = 0
            while self.is_running:
                try:
                    round_num += 1
                    print(f"جولة البحث #{round_num}")
                    
                    # توليد وفحص اليوزرات
                    usernames = self.generate_usernames(8)
                    found = []
                    
                    for username in usernames:
                        if self.check_username(username):
                            found.append(username)
                            self.save_username(username)
                        time.sleep(1)
                    
                    # إرسال النتائج
                    if found and bot_instance:
                        self.found_count += len(found)
                        message = f"🎉 عثرت على {len(found)} يوزر:\n"
                        for u in found:
                            message += f"• @{u}\n"
                        
                        asyncio.run_coroutine_threadsafe(
                            bot_instance.send_message(chat_id, message),
                            asyncio.get_event_loop()
                        )
                    
                    # تقرير كل 3 جولات
                    if round_num % 3 == 0:
                        report = f"📊 جولة #{round_num}\nتم فحص: {self.checked_count}\nتم العثور: {self.found_count}"
                        asyncio.run_coroutine_threadsafe(
                            bot_instance.send_message(chat_id, report),
                            asyncio.get_event_loop()
                        )
                    
                    time.sleep(10)
                    
                except Exception as e:
                    print(f"خطأ: {e}")
                    time.sleep(10)
        
        self.thread = threading.Thread(target=search_loop)
        self.thread.daemon = True
        self.thread.start()
        return True
    
    def stop_search(self):
        """إيقاف البحث"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        return True

# إنشاء البوت
bot = SimpleTikTokBot()

async def start(update, context):
    """بدء البوت"""
    await update.message.reply_text(
        "🎯 بوت يوزرات تيك توك\n\n"
        "الأوامر:\n"
        "/search - بحث سريع\n"
        "/auto - بحث تلقائي\n"
        "/stop - إيقاف البحث\n"
        "/list - المحفوظات\n"
        "/info - المعلومات"
    )

async def quick_search(update, context):
    """بحث سريع"""
    await update.message.reply_text("🔍 جاري البحث...")
    
    usernames = bot.generate_usernames(6)
    found = []
    
    for username in usernames:
        if bot.check_username(username):
            found.append(username)
            bot.save_username(username)
        time.sleep(1)
    
    if found:
        msg = "✅ اليوزرات المتاحة:\n"
        for u in found:
            msg += f"• @{u}\n"
    else:
        msg = "❌ لا توجد يوزرات متاحة"
    
    await update.message.reply_text(msg)

async def auto_start(update, context):
    """بدء التلقائي"""
    if bot.is_running:
        await update.message.reply_text("⚠️ البحث يعمل بالفعل")
        return
    
    if bot.start_auto_search(context.bot, update.message.chat_id):
        await update.message.reply_text("🚀 بدأ البحث التلقائي!")
    else:
        await update.message.reply_text("❌ فشل في البدء")

async def auto_stop(update, context):
    """إيقاف التلقائي"""
    if not bot.is_running:
        await update.message.reply_text("⚠️ البحث غير نشط")
        return
    
    bot.stop_search()
    await update.message.reply_text("⏹️ تم الإيقاف")

async def show_saved(update, context):
    """عرض المحفوظات"""
    saved = bot.load_saved()
    if saved:
        msg = "💾 المحفوظات:\n"
        for i, u in enumerate(saved[:10], 1):
            msg += f"{i}. @{u}\n"
        msg += f"\nالمجموع: {len(saved)}"
    else:
        msg = "💾 لا توجد محفوظات"
    
    await update.message.reply_text(msg)

async def show_info(update, context):
    """عرض المعلومات"""
    info = f"""
📊 معلومات البوت:
- تم فحص: {bot.checked_count}
- تم العثور: {bot.found_count}
- الحالة: {'🟢 نشط' if bot.is_running else '🔴 متوقف'}
- المحفوظات: {len(bot.load_saved())}
    """
    await update.message.reply_text(info)

def main():
    """الدالة الرئيسية"""
    try:
        # إنشاء التطبيق
        app = Application.builder().token(BOT_TOKEN).build()
        
        # إضافة الأوامر
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("search", quick_search))
        app.add_handler(CommandHandler("auto", auto_start))
        app.add_handler(CommandHandler("stop", auto_stop))
        app.add_handler(CommandHandler("list", show_saved))
        app.add_handler(CommandHandler("info", show_info))
        
        print("🤖 البوت يعمل الآن!")
        print("💬 أرسل /start للبوت")
        
        # بدء البوت
        app.run_polling()
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        time.sleep(30)
        main()

if __name__ == '__main__':
    main()
