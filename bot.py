import os
import requests
import random
import json
import logging
import time
import threading
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from fake_useragent import UserAgent

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# الحصول على التوكن من متغيرات البيئة
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN not found in environment variables!")
    exit(1)

class AdvancedTikTokChecker:
    def __init__(self):
        self.ua = UserAgent()
        self.checked_count = 0
        self.auto_search_running = False
        self.auto_search_thread = None
        self.last_notification_time = 0
        self.notification_cooldown = 10
        
    def check_tiktok_username(self, username):
        """فحص يوزر تيك توك باستخدام requests"""
        try:
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            
            url = f"https://www.tiktok.com/@{username}"
            
            response = requests.get(url, headers=headers, timeout=10)
            self.checked_count += 1
            
            if response.status_code == 404:
                logger.info(f"✅ متاح: @{username}")
                return True
            elif response.status_code == 200:
                return False
            else:
                return False
                
        except Exception as e:
            logger.error(f"خطأ في فحص {username}: {e}")
            return False
    
    def load_saved_usernames(self):
        """تحميل اليوزرات المحفوظة"""
        try:
            if os.path.exists("saved_usernames.json"):
                with open("saved_usernames.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"خطأ في تحميل المحفوظات: {e}")
            return []
    
    def save_username(self, username, chat_id=None, bot_instance=None):
        """حفظ اليوزر الجديد مع إشعار"""
        try:
            saved = self.load_saved_usernames()
            if username not in saved:
                saved.append(username)
                with open("saved_usernames.json", "w", encoding="utf-8") as f:
                    json.dump(saved, f, ensure_ascii=False, indent=2)
                logger.info(f"💾 تم حفظ اليوزر: @{username}")
                
                if chat_id and bot_instance:
                    # ✅ إصلاح: استخدام asyncio لاستدعاء الدالة غير المتزامنة
                    asyncio.create_task(
                        self.send_username_notification(chat_id, username, bot_instance)
                    )
                return True
            return False
        except Exception as e:
            logger.error(f"خطأ في الحفظ: {e}")
            return False
    
    async def send_username_notification(self, chat_id, username, bot_instance):
        """إرسال إشعار باليوزر الجديد - يجب أن تكون async"""
        try:
            current_time = time.time()
            if current_time - self.last_notification_time >= self.notification_cooldown:
                message = f"🎉 **تم العثور على يوزر جديد!**\n\n✅ `@{username}`\n💾 تم الحفظ تلقائياً"
                
                # ✅ ✅ ✅ التصحيح الأساسي: إضافة await هنا
                await bot_instance.send_message(chat_id=chat_id, text=message)
                
                self.last_notification_time = current_time
                return True
        except Exception as e:
            logger.error(f"خطأ في إرسال الإشعار: {e}")
        return False
    
    def generate_usernames(self, pattern="mixed", count=10):
        """توليد يوزرات للفحص"""
        saved = self.load_saved_usernames()
        
        if pattern == "numbers":
            base = [str(i).zfill(3) for i in range(100, 1000)]
        elif pattern == "letters":
            letters = 'abcdefghijklmnopqrstuvwxyz'
            base = [a+b+c for a in letters for b in letters for c in letters][:500]
        else:
            chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
            base = [''.join(random.choices(chars, k=3)) for _ in range(500)]
        
        filtered = [u for u in base if u not in saved]
        random.shuffle(filtered)
        return filtered[:count]
    
    def bulk_check(self, usernames, chat_id=None, bot_instance=None):
        """فحص مجموعة يوزرات مع إشعارات"""
        available = []
        newly_saved = []
        
        for username in usernames:
            try:
                is_available = self.check_tiktok_username(username)
                
                if is_available:
                    available.append(username)
                    if self.save_username(username, chat_id, bot_instance):
                        newly_saved.append(username)
                
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"خطأ في {username}: {e}")
                continue
        
        return available, newly_saved
    
    def start_auto_search(self, chat_id, bot_instance, search_type="mixed", batch_size=10, delay=3):
        """بدء البحث التلقائي المستمر مع إشعارات محسنة"""
        if self.auto_search_running:
            return False
        
        self.auto_search_running = True
        
        def auto_search_loop():
            round_count = 0
            total_found = 0
            
            try:
                # ✅ إصلاح: استخدام asyncio لاستدعاء الدالة غير المتزامنة
                asyncio.create_task(
                    self.send_auto_start_message(chat_id, bot_instance, search_type, batch_size, delay)
                )
            except Exception as e:
                logger.error(f"خطأ في إرسال رسالة البدء: {e}")
            
            while self.auto_search_running:
                try:
                    round_count += 1
                    logger.info(f"🔄 جولة البحث التلقائي #{round_count}")
                    
                    usernames = self.generate_usernames(search_type, batch_size)
                    available, saved = self.bulk_check(usernames, chat_id, bot_instance)
                    
                    total_found += len(available)
                    
                    if available:
                        message = (
                            f"✅ **تم العثور على {len(available)} يوزر في الجولة #{round_count}:**\n\n"
                        )
                        for username in available:
                            message += f"• `@{username}`\n"
                        message += f"\n💾 تم حفظ {len(saved)} يوزر جديد"
                        try:
                            asyncio.create_task(
                                bot_instance.send_message(chat_id=chat_id, text=message)
                            )
                        except Exception as e:
                            logger.error(f"خطأ في إرسال نتائج الجولة: {e}")
                    
                    if round_count % 10 == 0:
                        try:
                            asyncio.create_task(
                                self.send_progress_report(chat_id, bot_instance, round_count, total_found)
                            )
                        except Exception as e:
                            logger.error(f"خطأ في إرسال التقرير الدوري: {e}")
                    
                    if self.auto_search_running:
                        time.sleep(delay)
                        
                except Exception as e:
                    logger.error(f"خطأ في البحث التلقائي: {e}")
                    if self.auto_search_running:
                        time.sleep(delay)
        
        self.auto_search_thread = threading.Thread(target=auto_search_loop)
        self.auto_search_thread.daemon = True
        self.auto_search_thread.start()
        
        return True
    
    async def send_auto_start_message(self, chat_id, bot_instance, search_type, batch_size, delay):
        """إرسال رسالة بدء البحث التلقائي"""
        try:
            await bot_instance.send_message(
                chat_id=chat_id,
                text=(
                    f"🔄 **بدأ البحث التلقائي!**\n\n"
                    f"📊 الإعدادات:\n"
                    f"• النوع: {search_type}\n"
                    f"• اليوزرات لكل جولة: {batch_size}\n"
                    f"• التأخير بين الجولات: {delay} ثواني\n\n"
                    f"🎯 سأخبرك فوراً عند العثور على أي يوزر جديد!"
                )
            )
        except Exception as e:
            logger.error(f"خطأ في إرسال رسالة البدء: {e}")
    
    async def send_progress_report(self, chat_id, bot_instance, round_count, total_found):
        """إرسال تقرير التقدم"""
        try:
            await bot_instance.send_message(
                chat_id=chat_id,
                text=(
                    f"📊 **تقرير تقدم البحث (#{round_count})**\n\n"
                    f"🔄 الجولات المكتملة: {round_count}\n"
                    f"✅ اليوزرات التي تم العثور عليها: {total_found}\n"
                    f"🔍 اليوزرات المفحوصة: {self.checked_count}\n"
                    f"💾 إجمالي المحفوظات: {len(self.load_saved_usernames())}"
                )
            )
        except Exception as e:
            logger.error(f"خطأ في إرسال التقرير الدوري: {e}")
    
    def stop_auto_search(self):
        """إيقاف البحث التلقائي"""
        self.auto_search_running = False
        if self.auto_search_thread:
            self.auto_search_thread.join(timeout=5)
        return True

# إنشاء كائن الفاحص
checker = AdvancedTikTokChecker()
user_stats = {}

def update_user_stats(user_id, found_count=0):
    """تحديث إحصائيات المستخدم"""
    if user_id not in user_stats:
        user_stats[user_id] = {
            'requests': 0,
            'found_usernames': 0,
            'last_active': datetime.now()
        }
    
    user_stats[user_id]['requests'] += 1
    user_stats[user_id]['found_usernames'] += found_count
    user_stats[user_id]['last_active'] = datetime.now()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء البوت"""
    user_id = update.effective_user.id
    update_user_stats(user_id)
    
    welcome_text = """🎯 بوت الذكاء لليوزرات النادرة - التشغيل الدائم

🔄 **البوت الآن يعمل 24/7 على السيرفر**
- لا يحتاج لتشغيل يدوي
- يعمل بشكل مستمر
- إشعارات فورية

🔍 **الأوامر المتاحة:**
/quick - بحث سريع
/auto_start - بدء البحث التلقائي  
/auto_stop - إيقاف البحث التلقائي
/saved - اليوزرات المحفوظة
/stats - الإحصائيات

⚡ **جرب الآن:** /auto_start"""
    
    await update.message.reply_text(welcome_text)

async def quick_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بحث سريع"""
    user_id = update.effective_user.id
    update_user_stats(user_id)
    
    await update.message.reply_text("🔍 جاري البحث السريع...")
    
    try:
        usernames = checker.generate_usernames("mixed", 8)
        available, saved = checker.bulk_check(usernames, update.effective_chat.id, context.bot)
        
        if available:
            response_message = "✅ **اليوزرات المتاحة:**\n\n"
            for username in available:
                response_message += f"• `@{username}`\n"
            response_message += f"\n💾 تم حفظ {len(saved)} يوزر"
        else:
            response_message = "❌ لم أعثر على يوزرات متاحة"
            
        await update.message.reply_text(response_message)
        
    except Exception as e:
        logger.error(f"خطأ في البحث السريع: {e}")
        await update.message.reply_text("❌ حدث خطأ أثناء البحث")

async def auto_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء البحث التلقائي"""
    user_id = update.effective_user.id
    update_user_stats(user_id)
    
    if checker.auto_search_running:
        await update.message.reply_text("🔄 البحث التلقائي يعمل بالفعل!")
        return
    
    success = checker.start_auto_search(
        chat_id=update.effective_chat.id,
        bot_instance=context.bot,
        search_type="mixed",
        batch_size=10,
        delay=3
    )
    
    if success:
        await update.message.reply_text("🔄 تم بدء البحث التلقائي!")
    else:
        await update.message.reply_text("❌ فشل في بدء البحث التلقائي")

async def auto_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إيقاف البحث التلقائي"""
    user_id = update.effective_user.id
    update_user_stats(user_id)
    
    if not checker.auto_search_running:
        await update.message.reply_text("⏹️ البحث التلقائي غير مفعل!")
        return
    
    checker.stop_auto_search()
    await update.message.reply_text("⏹️ تم إيقاف البحث التلقائي")

async def show_saved(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض المحفوظات"""
    user_id = update.effective_user.id
    update_user_stats(user_id)
    
    saved = checker.load_saved_usernames()
    
    if saved:
        response_message = "💾 **اليوزرات المحفوظة:**\n\n"
        for i, username in enumerate(saved[:10], 1):
            response_message += f"{i}. `@{username}`\n"
        response_message += f"\n📊 المجموع: {len(saved)} يوزر"
    else:
        response_message = "💾 لا توجد يوزرات محفوظة"
    
    await update.message.reply_text(response_message)

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض الإحصائيات"""
    user_id = update.effective_user.id
    update_user_stats(user_id)
    
    saved_count = len(checker.load_saved_usernames())
    auto_status = "🟢 نشط" if checker.auto_search_running else "🔴 متوقف"
    
    response_message = f"""📊 **إحصائيات البوت**

💾 اليوزرات المحفوظة: {saved_count}
⚡ اليوزرات المفحوصة: {checker.checked_count}
🔄 البحث التلقائي: {auto_status}

🚀 البوت يعمل على السيرفر الدائم"""
    
    await update.message.reply_text(response_message)

def main():
    """الدالة الرئيسية"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # إضافة handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quick", quick_search))
    application.add_handler(CommandHandler("auto_start", auto_start))
    application.add_handler(CommandHandler("auto_stop", auto_stop))
    application.add_handler(CommandHandler("saved", show_saved))
    application.add_handler(CommandHandler("stats", show_stats))
    
    print("🚀 بوت يوزرات تيك توك يعمل على السيرفر!")
    print("⏰ التشغيل الدائم 24/7")
    
    # بدء البوت
    application.run_polling()

if __name__ == '__main__':
    main()
