import os
import requests
import random
import json
import time
import logging
import threading
import asyncio
from datetime import datetime
from telegram.ext import Application, CommandHandler, ContextTypes

# إعداد التسجيل المفصل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# التوكن
BOT_TOKEN = os.getenv('BOT_TOKEN', '8198990470:AAHjcpxW0oCXZZq4RL6pCN2II292iETc7Hc')

print("🚀 بدء تشغيل البوت الحقيقي...")
print(f"📝 طول التوكن: {len(BOT_TOKEN)}")

class RealTikTokChecker:
    def __init__(self):
        self.checked_count = 0
        self.auto_search_running = False
        self.auto_search_thread = None
        self.total_found = 0
        self.start_time = 0
        self.round_count = 0
        self.last_activity = time.time()
        logger.info("✅ النظام الحقيقي جاهز - سيفحص يوزرات حقيقية!")
        
    def real_check_username(self, username):
        """فحص حقيقي لليوزر - هذه المرة سيعمل!"""
        try:
            logger.info(f"🔍 جاري فحص @{username} حقيقة...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            url = f"https://www.tiktok.com/@{username}"
            
            # استخدم جلسة للتحكم أفضل
            session = requests.Session()
            session.headers.update(headers)
            
            response = session.get(url, timeout=15, allow_redirects=True)
            self.checked_count += 1
            self.last_activity = time.time()
            
            logger.info(f"📊 استجابة @{username}: {response.status_code}")
            
            # تحليل دقيق للاستجابة
            if response.status_code == 404:
                logger.info(f"🎉 @{username} متاح حقيقة!")
                return True
            elif response.status_code == 200:
                logger.info(f"❌ @{username} مستخدم")
                return False
            else:
                logger.warning(f"⚠️ @{username} حالة غير متوقعة: {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            logger.warning(f"⏰ انتهت المهلة لـ @{username}")
            return False
        except requests.exceptions.ConnectionError:
            logger.warning(f"🌐 خطأ اتصال لـ @{username}")
            return False
        except Exception as e:
            logger.error(f"🚨 خطأ غير متوقع في @{username}: {str(e)}")
            return False
    
    def load_saved(self):
        """تحميل المحفوظات"""
        try:
            if os.path.exists("saved.json"):
                with open("saved.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    logger.info(f"📁 تم تحميل {len(data)} يوزر محفوظ")
                    return data
            logger.info("📁 لا توجد محفوظات سابقة")
            return []
        except Exception as e:
            logger.error(f"❌ خطأ في تحميل المحفوظات: {e}")
            return []
    
    def save_username(self, username):
        """حفظ اليوزر"""
        try:
            saved = self.load_saved()
            if username not in saved:
                saved.append(username)
                with open("saved.json", "w", encoding="utf-8") as f:
                    json.dump(saved, f, ensure_ascii=False, indent=2)
                logger.info(f"💾 تم حفظ @{username} حقيقة في الملف!")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ خطأ في الحفظ: {e}")
            return False
    
    def generate_real_usernames(self, count=15):
        """توليد يوزرات حقيقية للفحص"""
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
        usernames = []
        
        # يوزرات 3 أحرف
        for _ in range(8):
            username = ''.join(random.choices(chars, k=3))
            usernames.append(username)
        
        # يوزرات 4 أحرف  
        for _ in range(7):
            username = ''.join(random.choices(chars, k=4))
            usernames.append(username)
        
        random.shuffle(usernames)
        logger.info(f"🔄 تم توليد {len(usernames)} يوزر للفحص")
        return usernames[:count]
    
    def real_bulk_check(self, usernames):
        """فحص مجموعة حقيقي"""
        available = []
        logger.info(f"🔍 بدء فحص {len(usernames)} يوزر...")
        
        for i, username in enumerate(usernames, 1):
            logger.info(f"📋 [{i}/{len(usernames)}] فحص @{username}...")
            
            if self.real_check_username(username):
                available.append(username)
                self.save_username(username)
                logger.info(f"✅ تمت إضافة @{username} للقائمة")
            
            # تأخير واقعي بين الطلبات
            if i < len(usernames):  # لا تنتظر بعد الأخير
                wait_time = random.uniform(1.5, 3.0)
                logger.info(f"⏳ انتظار {wait_time:.1f} ثانية...")
                time.sleep(wait_time)
        
        logger.info(f"🎯 انتهى الفحص: {len(available)} يوزر متاح")
        return available
    
    def start_real_search(self, bot_instance, chat_id):
        """بدء بحث حقيقي - هذه المرة سيعمل!"""
        if self.auto_search_running:
            logger.warning("⚠️ البحث يعمل بالفعل!")
            return False
        
        self.auto_search_running = True
        self.start_time = time.time()
        self.round_count = 0
        self.total_found = 0
        
        logger.info("🚀 بدء البحث التلقائي الحقيقي!")
        
        def real_search_loop():
            logger.info("🔄 بدء حلقة البحث الرئيسية...")
            
            while self.auto_search_running:
                try:
                    self.round_count += 1
                    current_round = self.round_count
                    
                    logger.info(f"🔄 الجولة #{current_round} - بدء الفحص الحقيقي")
                    
                    # تأكيد بدء الجولة
                    asyncio.run_coroutine_threadsafe(
                        self.send_round_start(bot_instance, chat_id, current_round),
                        asyncio.get_event_loop()
                    )
                    
                    # توليد وفحص اليوزرات حقيقة
                    usernames = self.generate_real_usernames(12)
                    logger.info(f"🔍 الجولة #{current_round}: فحص {len(usernames)} يوزر")
                    
                    available = self.real_bulk_check(usernames)
                    
                    # معالجة النتائج
                    if available:
                        self.total_found += len(available)
                        logger.info(f"🎉 الجولة #{current_round}: وجد {len(available)} يوزر!")
                        
                        asyncio.run_coroutine_threadsafe(
                            self.send_real_results(bot_instance, chat_id, available, current_round),
                            asyncio.get_event_loop()
                        )
                    else:
                        logger.info(f"🔍 الجولة #{current_round}: لا توجد يوزرات متاحة")
                        
                        # إشعار بعدم العثور
                        asyncio.run_coroutine_threadsafe(
                            self.send_no_results(bot_instance, chat_id, current_round),
                            asyncio.get_event_loop()
                        )
                    
                    # تقرير بعد كل جولة
                    asyncio.run_coroutine_threadsafe(
                        self.send_round_report(bot_instance, chat_id, current_round),
                        asyncio.get_event_loop()
                    )
                    
                    # انتظار واقعي بين الجولات
                    wait_time = 10
                    logger.info(f"⏳ انتظار {wait_time} ثواني للجولة التالية...")
                    for i in range(wait_time, 0, -1):
                        if not self.auto_search_running:
                            break
                        time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"🚨 خطأ في حلقة البحث: {e}")
                    time.sleep(10)
        
        # بدء البحث في thread منفصل
        try:
            self.auto_search_thread = threading.Thread(target=real_search_loop)
            self.auto_search_thread.daemon = True
            self.auto_search_thread.start()
            logger.info("✅ البحث التلقائي بدأ بنجاح!")
            return True
        except Exception as e:
            logger.error(f"❌ فشل في بدء البحث: {e}")
            return False
    
    async def send_round_start(self, bot_instance, chat_id, round_num):
        """إرسال تأكيد بدء الجولة"""
        try:
            await bot_instance.send_message(
                chat_id=chat_id,
                text=f"🔍 **بدء الجولة #{round_num}**\n\nجاري فحص اليوزرات حقيقة الآن..."
            )
        except Exception as e:
            logger.error(f"❌ خطأ في إرسال بدء الجولة: {e}")
    
    async def send_real_results(self, bot_instance, chat_id, available, round_num):
        """إرسال نتائج حقيقية"""
        try:
            three_char = [u for u in available if len(u) == 3]
            four_char = [u for u in available if len(u) == 4]
            
            message = f"🎉 **تم العثور على {len(available)} يوزر في الجولة #{round_num}!**\n\n"
            
            if three_char:
                message += "🎯 **يوزرات 3 أحرف (نادرة):**\n"
                for username in three_char:
                    message += f"• `@{username}`\n"
                message += "\n"
            
            if four_char:
                message += "⭐ **يوزرات 4 أحرف (مميزة):**\n"
                for username in four_char:
                    message += f"• `@{username}`\n"
            
            message += f"\n💾 تم الحفظ تلقائياً في الملف"
            
            await bot_instance.send_message(chat_id=chat_id, text=message)
            
        except Exception as e:
            logger.error(f"❌ خطأ في إرسال النتائج: {e}")
    
    async def send_no_results(self, bot_instance, chat_id, round_num):
        """إرسال إشعار بعدم العثور"""
        try:
            await bot_instance.send_message(
                chat_id=chat_id,
                text=f"🔍 **الجولة #{round_num}**\n\nلم أعثر على يوزرات متاحة في هذه الجولة.\n\nلا تزال الجولات مستمرة..."
            )
        except Exception as e:
            logger.error(f"❌ خطأ في إرسال عدم العثور: {e}")
    
    async def send_round_report(self, bot_instance, chat_id, round_num):
        """إرسال تقرير الجولة"""
        try:
            uptime = int(time.time() - self.start_time)
            minutes = uptime // 60
            seconds = uptime % 60
            
            saved_count = len(self.load_saved())
            
            message = (
                f"📊 **تقرير الجولة #{round_num}**\n\n"
                f"⏰ وقت التشغيل: {minutes} دقيقة {seconds} ثانية\n"
                f"🔄 الجولات المكتملة: {round_num}\n"
                f"🎯 اليوزرات المكتشفة: {self.total_found}\n"
                f"🔍 اليوزرات المفحوصة: {self.checked_count}\n"
                f"💾 المحفوظات الإجمالية: {saved_count}\n\n"
                f"✅ البوت يعمل ويفحص حقيقة!"
            )
            
            await bot_instance.send_message(chat_id=chat_id, text=message)
            
        except Exception as e:
            logger.error(f"❌ خطأ في إرسال التقرير: {e}")
    
    def stop_real_search(self):
        """إيقاف البحث الحقيقي"""
        self.auto_search_running = False
        try:
            if self.auto_search_thread:
                self.auto_search_thread.join(timeout=10)
            logger.info("✅ البحث التلقائي توقف")
            return True
        except Exception as e:
            logger.error(f"❌ خطأ في الإيقاف: {e}")
            return False

# إنشاء كائن حقيقي
checker = RealTikTokChecker()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء البوت - إصدار حقيقي"""
    welcome_text = """🎯 **بوت اليوزرات النادرة - الإصدار الحقيقي**

✅ **هذا الإصدار:**
• يفحص يوزرات حقيقية على تيك توك
• يعرض تقارير فعلية عن الفحص
• يحفظ اليوزرات في ملف فعلي
• يرصد النتائج الحقيقية

⚡ **الأوامر المتاحة:**
/quick - فحص سريع حقيقي
/auto_start - بحث تلقائي حقيقي
/auto_stop - إيقاف البحث
/saved - عرض المحفوظات الحقيقية
/stats - إحصائيات فعلية
/status - حالة النظام

🚀 **جرب الآن:** /quick للفحص الفعلي"""
    
    await update.message.reply_text(welcome_text)

async def quick_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بحث سريع حقيقي"""
    await update.message.reply_text("🔍 **جاري فحص سريع حقيقي...**\n\nسأفحص 8 يوزرات وسأخبرك بالنتيجة الفعلية!")
    
    try:
        # فحص حقيقي
        usernames = checker.generate_real_usernames(8)
        available = checker.real_bulk_check(usernames)
        
        if available:
            msg = "✅ **تم الفحص الحقيقي! اليوزرات المتاحة:**\n\n"
            for u in available:
                msg += f"• `@{u}`\n"
            msg += f"\n💾 تم حفظ {len(available)} يوزر في الملف"
        else:
            msg = "🔍 **تم الفحص الحقيقي!**\n\nلم أعثر على يوزرات متاحة في هذه المجموعة.\n\n🔄 جرب البحث التلقائي: /auto_start"
        
        await update.message.reply_text(msg)
        
    except Exception as e:
        logger.error(f"❌ خطأ في البحث السريع: {e}")
        await update.message.reply_text("⚠️ حدث خطأ أثناء الفحص الحقيقي")

async def auto_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء البحث التلقائي الحقيقي"""
    if checker.auto_search_running:
        await update.message.reply_text("🔄 البحث التلقائي يعمل بالفعل!")
        return
    
    success = checker.start_real_search(
        bot_instance=context.bot,
        chat_id=update.effective_chat.id
    )
    
    if success:
        await update.message.reply_text(
            "🚀 **تم بدء النظام التلقائي الحقيقي!**\n\n"
            "✅ البوت يفحص يوزرات حقيقية الآن\n"
            "🔍 سأخبرك بنتائج كل جولة\n"
            "📊 تقارير فعلية عن الفحص\n"
            "🎯 إشعارات حقيقية عند الاكتشاف\n\n"
            "⏰ الجولة الأولى تبدأ الآن..."
        )
    else:
        await update.message.reply_text("❌ فشل في بدء البحث التلقائي")

async def auto_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إيقاف البحث الحقيقي"""
    if not checker.auto_search_running:
        await update.message.reply_text("⏹️ البحث التلقائي غير مفعل!")
        return
    
    checker.stop_real_search()
    
    uptime = int(time.time() - checker.start_time)
    minutes = uptime // 60
    seconds = uptime % 60
    
    saved_count = len(checker.load_saved())
    
    await update.message.reply_text(
        f"⏹️ **تم إيقاف البحث التلقائي**\n\n"
        f"📊 **التقرير النهائي الحقيقي:**\n"
        f"• وقت التشغيل: {minutes} دقيقة {seconds} ثانية\n"
        f"• الجولات المكتملة: {checker.round_count}\n"
        f"• اليوزرات المفحوصة: {checker.checked_count}\n"
        f"• اليوزرات المكتشفة: {checker.total_found}\n"
        f"• المحفوظات الإجمالية: {saved_count}\n\n"
        f"✅ الفحص كان حقيقياً وتم حفظ النتائج!"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حالة النظام الحقيقية"""
    status_msg = "🟢 **حالة النظام الحقيقية**\n\n"
    
    if checker.auto_search_running:
        uptime = int(time.time() - checker.start_time)
        minutes = uptime // 60
        seconds = uptime % 60
        
        status_msg += (
            f"✅ **البحث التلقائي نشط**\n"
            f"⏰ التشغيل: {minutes}د {seconds}ث\n"
            f"🔄 الجولات: {checker.round_count}\n"
            f"🎯 المكتشف: {checker.total_found}\n"
            f"🔍 المفحوص: {checker.checked_count}\n"
            f"💾 المحفوظات: {len(checker.load_saved())}\n\n"
            f"🚀 البوت يفحص يوزرات حقيقية الآن!"
        )
    else:
        status_msg += (
            "🔴 **البحث التلقائي متوقف**\n\n"
            "▶️ استخدم /auto_start لبدء الفحص الحقيقي"
        )
    
    await update.message.reply_text(status_msg)

async def saved(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض المحفوظات الحقيقية"""
    saved = checker.load_saved()
    
    if saved:
        three_char = [u for u in saved if len(u) == 3]
        four_char = [u for u in saved if len(u) == 4]
        
        msg = "💾 **اليوزرات المحفوظة (حقيقية):**\n\n"
        
        if three_char:
            msg += "🎯 **3 أحرف:**\n"
            for i, u in enumerate(three_char[:8], 1):
                msg += f"{i}. `@{u}`\n"
            msg += f"→ إجمالي: {len(three_char)} يوزر\n\n"
        
        if four_char:
            msg += "⭐ **4 أحرف:**\n"
            for i, u in enumerate(four_char[:8], 1):
                msg += f"{i}. `@{u}`\n"
            msg += f"→ إجمالي: {len(four_char)} يوزر\n\n"
        
        msg += f"📊 **المجموع الكلي: {len(saved)} يوزر**\n\n"
        msg += "✅ هذه محفوظات حقيقية من الفحص"
        
    else:
        msg = "💾 لا توجد يوزرات محفوظة\n\n🔍 ابدأ بالفحص الحقيقي: /quick"
    
    await update.message.reply_text(msg)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إحصائيات حقيقية"""
    saved = checker.load_saved()
    
    stats_msg = (
        f"📊 **إحصائيات حقيقية**\n\n"
        f"💾 المحفوظات: {len(saved)} يوزر\n"
        f"🔍 المفحوصة: {checker.checked_count}\n"
        f"🎯 المكتشفة: {checker.total_found}\n"
        f"🔄 حالة البحث: {'🟢 نشط' if checker.auto_search_running else '🔴 متوقف'}\n\n"
        f"✅ **هذه إحصائيات فعلية من الفحص الحقيقي**\n"
        f"🚀 البوت يعمل ويفحص يوزرات حقيقية!"
    )
    
    await update.message.reply_text(stats_msg)

def main():
    """الدالة الرئيسية الحقيقية"""
    try:
        print("🚀 بدء تشغيل البوت الحقيقي...")
        print("✅ سيفحص يوزرات حقيقية على تيك توك")
        print("📊 سيعرض نتائج فعلية")
        print("💾 سيحفظ في ملف حقيقي")
        
        # إنشاء التطبيق
        application = Application.builder().token(BOT_TOKEN).build()
        
        # إضافة الأوامر
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("quick", quick_search))
        application.add_handler(CommandHandler("auto_start", auto_start))
        application.add_handler(CommandHandler("auto_stop", auto_stop))
        application.add_handler(CommandHandler("saved", saved))
        application.add_handler(CommandHandler("stats", stats))
        application.add_handler(CommandHandler("status", status))
        
        print("🎯 البوت الحقيقي جاهز للفحص!")
        print("🤖 إرسل /quick للبدء في الفحص الحقيقي")
        
        # تشغيل البوت
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ فشل في تشغيل البوت: {e}")
        print(f"❌ الخطأ: {e}")

if __name__ == '__main__':
    main()
