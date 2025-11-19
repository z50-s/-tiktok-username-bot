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

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# التوكن
BOT_TOKEN = os.getenv('BOT_TOKEN', '8198990470:AAHjcpxW0oCXZZq4RL6pCN2II292iETc7Hc')

class AdvancedTikTokChecker:
    def __init__(self):
        self.checked_count = 0
        self.auto_search_running = False
        self.auto_search_thread = None
        self.last_notification_time = 0
        self.notification_cooldown = 5
        self.last_round_time = 0
        self.consecutive_empty_rounds = 0
        self.total_found = 0
        self.start_time = time.time()
        print("✅ النظام المتقدم لليوزرات القصيرة جاهز")
        
    def check_username(self, username):
        """فحص يوزر تيك توك"""
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
        """تحميل المحفوظات"""
        try:
            if os.path.exists("saved.json"):
                with open("saved.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"خطأ في تحميل المحفوظات: {e}")
            return []
    
    def save_username(self, username):
        """حفظ اليوزر"""
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
    
    def generate_smart_usernames(self, count=15):
        """توليد يوزرات ذكية مع أولوية للقيمة"""
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
        usernames = []
        
        # 1. يوزرات 3 أحرف - الأعلى قيمة
        three_char = [''.join(random.choices(chars, k=3)) for _ in range(8)]
        
        # 2. يوزرات 4 أحرف - قيمة عالية
        four_char = [''.join(random.choices(chars, k=4)) for _ in range(7)]
        
        # دمج وخلط
        usernames = three_char + four_char
        random.shuffle(usernames)
        
        return usernames[:count]
    
    def bulk_check(self, usernames):
        """فحص مجموعة يوزرات"""
        available = []
        for username in usernames:
            # تأكد أن اليوزر بين 3-4 أحرف فقط
            if 3 <= len(username) <= 4 and username.isalnum():
                if self.check_username(username):
                    available.append(username)
                    self.save_username(username)
            time.sleep(1)  # تأخير بين الطلبات
        return available
    
    def start_auto_search(self, bot_instance, chat_id):
        """بدء البحث التلقائي المستمر لليوزرات القصيرة"""
        if self.auto_search_running:
            return False
        
        self.auto_search_running = True
        self.start_time = time.time()
        self.consecutive_empty_rounds = 0
        
        def auto_search_loop():
            round_count = 0
            total_found = 0
            
            # إرسال رسالة تأكيد البدء
            asyncio.run_coroutine_threadsafe(
                self.send_startup_confirmation(bot_instance, chat_id),
                asyncio.get_event_loop()
            )
            
            while self.auto_search_running:
                try:
                    round_count += 1
                    logger.info(f"🔄 جولة البحث التلقائي #{round_count}")
                    
                    # توليد وفحص اليوزرات المميزة
                    usernames = self.generate_smart_usernames(12)
                    available = self.bulk_check(usernames)
                    
                    # تحديث الإحصائيات
                    if available:
                        total_found += len(available)
                        self.total_found = total_found
                        self.consecutive_empty_rounds = 0
                        
                        # إرسال إشعار اليوزرات الجديدة
                        asyncio.run_coroutine_threadsafe(
                            self.send_found_notification(bot_instance, chat_id, available, round_count),
                            asyncio.get_event_loop()
                        )
                    else:
                        self.consecutive_empty_rounds += 1
                        
                        # إرسال تقرير طمأنة كل 3 جولات فارغة
                        if self.consecutive_empty_rounds % 3 == 0:
                            asyncio.run_coroutine_threadsafe(
                                self.send_reassurance_report(bot_instance, chat_id, round_count, total_found),
                                asyncio.get_event_loop()
                            )
                    
                    # تقرير أداء كل 5 جولات
                    if round_count % 5 == 0:
                        asyncio.run_coroutine_threadsafe(
                            self.send_performance_report(bot_instance, chat_id, round_count, total_found),
                            asyncio.get_event_loop()
                        )
                    
                    # تأكيد الاستمرارية كل 10 جولات
                    if round_count % 10 == 0:
                        asyncio.run_coroutine_threadsafe(
                            self.send_continuity_confirmation(bot_instance, chat_id, round_count),
                            asyncio.get_event_loop()
                        )
                    
                    # انتظار قبل الجولة التالية
                    time.sleep(8)
                    
                except Exception as e:
                    logger.error(f"خطأ في البحث التلقائي: {e}")
                    time.sleep(10)
        
        # بدء البحث في thread منفصل
        self.auto_search_thread = threading.Thread(target=auto_search_loop)
        self.auto_search_thread.daemon = True
        self.auto_search_thread.start()
        return True
    
    async def send_startup_confirmation(self, bot_instance, chat_id):
        """إرسال تأكيد بدء التشغيل"""
        try:
            await bot_instance.send_message(
                chat_id=chat_id,
                text=(
                    "🚀 **تم بدء النظام التلقائي بنجاح!**\n\n"
                    "✅ البوت الآن يعمل بشكل مستمر\n"
                    "🔍 يبحث عن يوزرات 3-4 أحرف\n"
                    "📊 سأرسل تقارير دورية\n"
                    "🎯 وسأخبرك فوراً باكتشاف أي يوزر\n\n"
                    "⏰ الجولة الأولى تبدأ الآن..."
                )
            )
        except Exception as e:
            logger.error(f"خطأ في إرسال تأكيد البدء: {e}")
    
    async def send_found_notification(self, bot_instance, chat_id, available, round_count):
        """إرسال إشعار عند العثور على يوزرات"""
        try:
            # تصنيف اليوزرات حسب الطول
            three_char = [u for u in available if len(u) == 3]
            four_char = [u for u in available if len(u) == 4]
            
            message = f"🎉 **تم العثور على {len(available)} يوزر في الجولة #{round_count}!**\n\n"
            
            if three_char:
                message += f"🎯 **يوزرات 3 أحرف (نادرة):**\n"
                for username in three_char:
                    message += f"• `@{username}`\n"
                message += "\n"
            
            if four_char:
                message += f"⭐ **يوزرات 4 أحرف (مميزة):**\n"
                for username in four_char:
                    message += f"• `@{username}`\n"
            
            message += f"\n💾 تم الحفظ تلقائياً في قاعدة البيانات"
            
            await bot_instance.send_message(chat_id=chat_id, text=message)
            
        except Exception as e:
            logger.error(f"خطأ في إرسال إشعار الاكتشاف: {e}")
    
    async def send_reassurance_report(self, bot_instance, chat_id, round_count, total_found):
        """إرسال تقرير طمأنة عندما لا توجد يوزرات"""
        try:
            uptime_minutes = int((time.time() - self.start_time) / 60)
            
            await bot_instance.send_message(
                chat_id=chat_id,
                text=(
                    f"🔍 **تقرير طمأنة - الجولة #{round_count}**\n\n"
                    f"📊 البوت لا يزال يعمل بنشاط!\n"
                    f"⏰ وقت التشغيل: {uptime_minutes} دقيقة\n"
                    f"✅ تم العثور على: {total_found} يوزر حتى الآن\n"
                    f"🔄 الجولات المستمرة: {round_count}\n\n"
                    f"🎯 أستمر في البحث عن اليوزرات النادرة..."
                )
            )
        except Exception as e:
            logger.error(f"خطأ في إرسال تقرير الطمأنة: {e}")
    
    async def send_performance_report(self, bot_instance, chat_id, round_count, total_found):
        """إرسال تقرير أداء دوري"""
        try:
            uptime_minutes = int((time.time() - self.start_time) / 60)
            saved_count = len(self.load_saved())
            
            await bot_instance.send_message(
                chat_id=chat_id,
                text=(
                    f"📊 **تقرير الأداء (#{round_count})**\n\n"
                    f"🔄 الجولات المكتملة: {round_count}\n"
                    f"✅ اليوزرات المكتشفة: {total_found}\n"
                    f"🔍 اليوزرات المفحوصة: {self.checked_count}\n"
                    f"💾 المحفوظات الإجمالية: {saved_count}\n"
                    f"⏰ وقت التشغيل: {uptime_minutes} دقيقة\n\n"
                    f"⚡ البوت يعمل بشكل مثالي!"
                )
            )
        except Exception as e:
            logger.error(f"خطأ في إرسال تقرير الأداء: {e}")
    
    async def send_continuity_confirmation(self, bot_instance, chat_id, round_count):
        """إرسال تأكيد الاستمرارية"""
        try:
            uptime_hours = round((time.time() - self.start_time) / 3600, 1)
            
            await bot_instance.send_message(
                chat_id=chat_id,
                text=(
                    f"✅ **تأكيد الاستمرارية - الجولة #{round_count}**\n\n"
                    f"🎯 النظام يعمل بدون توقف\n"
                    f"⏰ وقت التشغيل: {uptime_hours} ساعة\n"
                    f"🔄 {round_count} جولة مكتملة\n"
                    f"📈 أداء مستقر ومستمر\n\n"
                    f"🚀 أستمر في البحث عن اليوزرات النادرة!"
                )
            )
        except Exception as e:
            logger.error(f"خطأ في إرسال تأكيد الاستمرارية: {e}")
    
    def stop_auto_search(self):
        """إيقاف البحث التلقائي"""
        self.auto_search_running = False
        if self.auto_search_thread:
            self.auto_search_thread.join(timeout=5)
        return True

# إنشاء كائن الفاحص
checker = AdvancedTikTokChecker()

async def start(update, context):
    """بدء البوت مع واجهة مخصصة لليوزرات القصيرة"""
    welcome_text = """🎯 **بوت اليوزرات النادرة (3-4 أحرف فقط)**

⚡ **نظام التأكيد والاستمرارية:**
✅ تأكيد بدء التشغيل فوراً
📊 تقارير أداء كل 5 جولات  
🔍 تقارير طمأنة عندما لا توجد يوزرات
✅ تأكيد الاستمرارية كل 10 جولات
🎯 إشعارات فورية عند الاكتشاف

🔍 **الأوامر المتاحة:**
/quick - بحث سريع عن اليوزرات القصيرة
/auto_start - بحث تلقائي مستمر مع تقارير
/auto_stop - إيقاف البحث التلقائي
/saved - عرض اليوزرات المحفوظة
/stats - الإحصائيات المتقدمة
/status - حالة النظام الحية

🚀 **الأنسب:** `/auto_start` - للبحث المستمر مع التأكيدات"""
    
    await update.message.reply_text(welcome_text)

async def quick_search(update, context):
    """بحث سريع عن اليوزرات القصيرة"""
    await update.message.reply_text("🔍 جاري البحث عن اليوزرات القصيرة (3-4 أحرف)...")
    
    try:
        usernames = checker.generate_smart_usernames(10)
        available = checker.bulk_check(usernames)
        
        if available:
            # فصل اليوزرات حسب الطول
            three_char = [u for u in available if len(u) == 3]
            four_char = [u for u in available if len(u) == 4]
            
            msg = "✅ **اليوزرات القصيرة المتاحة:**\n\n"
            
            if three_char:
                msg += "🎯 **يوزرات 3 أحرف (نادرة):**\n"
                for u in three_char:
                    msg += f"• `@{u}`\n"
                msg += "\n"
            
            if four_char:
                msg += "⭐ **يوزرات 4 أحرف (مميزة):**\n"
                for u in four_char:
                    msg += f"• `@{u}`\n"
            
            msg += f"\n💾 تم حفظ {len(available)} يوزر جديد"
        else:
            msg = "❌ لم أعثر على يوزرات قصيرة متاحة\n\n🔁 جرب البحث التلقائي: /auto_start"
            
        await update.message.reply_text(msg)
        
    except Exception as e:
        logger.error(f"خطأ في البحث السريع: {e}")
        await update.message.reply_text("❌ حدث خطأ أثناء البحث")

async def auto_start(update, context):
    """بدء البحث التلقائي لليوزرات القصيرة"""
    if checker.auto_search_running:
        await update.message.reply_text("🔄 البحث التلقائي يعمل بالفعل!")
        return
    
    success = checker.start_auto_search(
        bot_instance=context.bot,
        chat_id=update.effective_chat.id
    )
    
    if success:
        await update.message.reply_text(
            "🎯 **تم تفعيل النظام التلقائي المتقدم!**\n\n"
            "✅ ستصلك التأكيدات التالية:\n"
            "• تأكيد البدء فوراً ✅\n"
            "• تقارير أداء كل 5 جولات 📊\n"
            "• تقارير طمأنة دورية 🔍\n"
            "• تأكيد الاستمرارية كل 10 جولات ✅\n"
            "• إشعارات فورية عند الاكتشاف 🎯\n\n"
            "🚀 النظام يعمل الآن بشكل مستمر!"
        )
    else:
        await update.message.reply_text("❌ فشل في بدء البحث التلقائي")

async def auto_stop(update, context):
    """إيقاف البحث التلقائي"""
    if not checker.auto_search_running:
        await update.message.reply_text("⏹️ البحث التلقائي غير مفعل!")
        return
    
    saved_before = len(checker.load_saved())
    checker.stop_auto_search()
    
    # انتظار قليلاً ثم حساب اليوزرات الجديدة
    time.sleep(2)
    saved_after = len(checker.load_saved())
    new_saved = saved_after - saved_before
    
    uptime_seconds = time.time() - checker.start_time
    uptime_minutes = int(uptime_seconds / 60)
    
    await update.message.reply_text(
        "⏹️ **تم إيقاف النظام التلقائي**\n\n"
        f"📊 **التقرير النهائي:**\n"
        f"• وقت التشغيل: {uptime_minutes} دقيقة\n"
        f"• اليوزرات المفحوصة: {checker.checked_count}\n"
        f"• اليوزرات المحفوظة: {saved_after}\n"
        f"• اليوزرات الجديدة: {new_saved}\n"
        f"• إجمالي المكتشف: {checker.total_found}\n\n"
        "💾 لعرض اليوزرات: /saved\n"
        "▶️ للبدء مجدداً: /auto_start"
    )

async def status(update, context):
    """عرض حالة النظام الحية"""
    if not checker.auto_search_running:
        await update.message.reply_text("🔴 النظام التلقائي متوقف\n\n▶️ استخدم /auto_start للبدء")
        return
    
    uptime_seconds = time.time() - checker.start_time
    uptime_minutes = int(uptime_seconds / 60)
    uptime_hours = round(uptime_seconds / 3600, 1)
    
    status_text = f"""🟢 **حالة النظام الحية**

✅ النظام يعمل بشكل مستمر
⏰ وقت التشغيل: {uptime_minutes} دقيقة ({uptime_hours} ساعة)
🔄 الجولات الناجحة: مستمرة
📊 اليوزرات المفحوصة: {checker.checked_count}
🎯 المكتشف: {checker.total_found} يوزر
💾 المحفوظات: {len(checker.load_saved())}

🔍 **التقارير القادمة:**
• تقرير أداء كل 5 جولات
• تأكيد استمرارية كل 10 جولات  
• إشعار فوري عند الاكتشاف

🚀 النظام في أفضل حالة!"""
    
    await update.message.reply_text(status_text)

async def saved(update, context):
    """عرض المحفوظات مع تصنيف اليوزرات القصيرة"""
    saved = checker.load_saved()
    
    if saved:
        # تحليل المحفوظات
        three_char = [u for u in saved if len(u) == 3]
        four_char = [u for u in saved if len(u) == 4]
        
        msg = "💾 **اليوزرات المحفوظة:**\n\n"
        
        if three_char:
            msg += "🎯 **يوزرات 3 أحرف (نادرة):**\n"
            for i, u in enumerate(three_char[:10], 1):
                msg += f"{i}. `@{u}`\n"
            if len(three_char) > 10:
                msg += f"... و {len(three_char)-10} يوزر إضافي\n"
            msg += "\n"
        
        if four_char:
            msg += "⭐ **يوزرات 4 أحرف (مميزة):**\n"
            for i, u in enumerate(four_char[:10], 1):
                msg += f"{i}. `@{u}`\n"
            if len(four_char) > 10:
                msg += f"... و {len(four_char)-10} يوزر إضافي\n"
        
        msg += f"\n📊 **الإحصائيات:**\n"
        msg += f"• الإجمالي: {len(saved)} يوزر\n"
        msg += f"• يوزرات 3 أحرف: {len(three_char)} 🎯\n"
        msg += f"• يوزرات 4 أحرف: {len(four_char)} ⭐"
        
    else:
        msg = "💾 لا توجد يوزرات محفوظة\n\n🔍 ابدأ بالبحث: /auto_start"
    
    await update.message.reply_text(msg)

async def stats(update, context):
    """عرض الإحصائيات المتقدمة"""
    saved = checker.load_saved()
    auto_status = "🟢 نشط" if checker.auto_search_running else "🔴 متوقف"
    
    # تحليل متقدم لليوزرات
    three_char = [u for u in saved if len(u) == 3]
    four_char = [u for u in saved if len(u) == 4]
    
    if checker.auto_search_running:
        uptime_seconds = time.time() - checker.start_time
        uptime_str = f"{int(uptime_seconds/60)} دقيقة"
    else:
        uptime_str = "غير نشط"
    
    msg = f"""📊 **إحصائيات متقدمة**

💾 **المحفوظات:**
• الإجمالي: {len(saved)} يوزر
• يوزرات 3 أحرف: {len(three_char)} 🎯
• يوزرات 4 أحرف: {len(four_char)} ⭐

⚡ **الأداء:**
• اليوزرات المفحوصة: {checker.checked_count}
• اليوزرات المكتشفة: {checker.total_found}
• البحث التلقائي: {auto_status}
• وقت التشغيل: {uptime_str}

🎯 **النظام:**
• التأكيدات: نشطة ✅
• التقارير: دورية 📊
• الإشعارات: فورية 🚀"""
    
    await update.message.reply_text(msg)

def main():
    """الدالة الرئيسية"""
    try:
        print("🚀 بدء تشغيل بوت اليوزرات القصيرة المتقدم...")
        print("🎯 نظام التأكيد والاستمرارية مفعل")
        print("📊 التقارير الدورية نشطة")
        
        # إنشاء التطبيق
        application = Application.builder().token(BOT_TOKEN).build()
        
        # إضافة جميع الأوامر
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("quick", quick_search))
        application.add_handler(CommandHandler("auto_start", auto_start))
        application.add_handler(CommandHandler("auto_stop", auto_stop))
        application.add_handler(CommandHandler("saved", saved))
        application.add_handler(CommandHandler("stats", stats))
        application.add_handler(CommandHandler("status", status))
        
        print("✅ البوت المتقدم جاهز للتشغيل!")
        print("🎯 يركز على اليوزرات القصيرة (3-4 أحرف)")
        print("📊 نظام التأكيد والتقارير مفعل")
        print("🤖 إرسل /start للبوت للبدء")
        
        # تشغيل البوت
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ فشل في تشغيل البوت: {e}")
        print(f"❌ الخطأ: {e}")

if __name__ == '__main__':
    main()
