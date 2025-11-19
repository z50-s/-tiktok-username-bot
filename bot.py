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
        self.notification_cooldown = 5  # 5 ثواني بين الإشعارات
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
    
    def generate_premium_usernames(self, count=20):
        """توليد يوزرات مميزة (3-4 أحرف/أرقام فقط)"""
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
        premium_usernames = []
        
        # يوزرات 3 أحرف - الأكثر ندرة
        for _ in range(count // 2):
            username = ''.join(random.choices(chars, k=3))
            premium_usernames.append(username)
        
        # يوزرات 4 أحرف - نادرة أيضاً
        for _ in range(count // 2):
            username = ''.join(random.choices(chars, k=4))
            premium_usernames.append(username)
        
        # خلط القائمة وإزالة المكرر
        random.shuffle(premium_usernames)
        return list(dict.fromkeys(premium_usernames))[:count]
    
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
        
        def auto_search_loop():
            round_count = 0
            total_found = 0
            
            while self.auto_search_running:
                try:
                    round_count += 1
                    logger.info(f"🔄 جولة البحث التلقائي #{round_count}")
                    
                    # توليد وفحص اليوزرات المميزة
                    usernames = self.generate_smart_usernames(12)
                    available = self.bulk_check(usernames)
                    
                    # إرسال إشعار إذا وجد يوزرات
                    if available and bot_instance:
                        total_found += len(available)
                        
                        # تصنيف اليوزرات حسب الطول
                        three_char = [u for u in available if len(u) == 3]
                        four_char = [u for u in available if len(u) == 4]
                        
                        message = f"🎉 **تم العثور على {len(available)} يوزر جديد!**\n\n"
                        
                        if three_char:
                            message += f"🎯 **يوزرات 3 أحرف (نادرة):**\n"
                            for username in three_char:
                                message += f"• `@{username}`\n"
                            message += "\n"
                        
                        if four_char:
                            message += f"⭐ **يوزرات 4 أحرف (مميزة):**\n"
                            for username in four_char:
                                message += f"• `@{username}`\n"
                        
                        message += f"\n💾 تم الحفظ تلقائياً"
                        
                        # إرسال الإشعار
                        asyncio.run_coroutine_threadsafe(
                            bot_instance.send_message(chat_id=chat_id, text=message),
                            asyncio.get_event_loop()
                        )
                    
                    # تقرير كل 5 جولات
                    if round_count % 5 == 0:
                        report_msg = (
                            f"📊 **تقرير تقدم البحث (#{round_count})**\n\n"
                            f"🔄 الجولات المكتملة: {round_count}\n"
                            f"✅ اليوزرات التي تم العثور عليها: {total_found}\n"
                            f"🔍 اليوزرات المفحوصة: {self.checked_count}\n"
                            f"💾 إجمالي المحفوظات: {len(self.load_saved())}"
                        )
                        asyncio.run_coroutine_threadsafe(
                            bot_instance.send_message(chat_id=chat_id, text=report_msg),
                            asyncio.get_event_loop()
                        )
                    
                    # انتظار قبل الجولة التالية
                    time.sleep(8)  # 8 ثواني بين الجولات
                    
                except Exception as e:
                    logger.error(f"خطأ في البحث التلقائي: {e}")
                    time.sleep(10)
        
        # بدء البحث في thread منفصل
        self.auto_search_thread = threading.Thread(target=auto_search_loop)
        self.auto_search_thread.daemon = True
        self.auto_search_thread.start()
        return True
    
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

⚡ **مخصص للبحث عن:**
• يوزرات 3 أحرف/أرقام 🎯 (نادرة جداً)
• يوزرات 4 أحرف/أرقام ⭐ (مميزة)

🔍 **الأوامر المتاحة:**
/quick - بحث سريع عن اليوزرات القصيرة
/auto_start - بحث تلقائي مستمر
/auto_stop - إيقاف البحث التلقائي
/saved - عرض اليوزرات المحفوظة
/stats - الإحصائيات المتقدمة

🚀 **الأنسب:** `/auto_start` - للبحث المستمر عن اليوزرات النادرة"""
    
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
            "🎯 **تم بدء البحث التلقائي لليوزرات القصيرة!**\n\n"
            "🔍 **سأبحث عن:**\n"
            "• يوزرات 3 أحرف/أرقام 🎯 (نادرة)\n"
            "• يوزرات 4 أحرف/أرقام ⭐ (مميزة)\n\n"
            "⏰ **معدل البحث:**\n"
            "• بحث كل 8 ثواني\n"
            "• 12 يوزر لكل جولة\n"
            "• إشعارات فورية\n\n"
            "⏹️ للإيقاف: /auto_stop"
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
    
    await update.message.reply_text(
        "⏹️ **تم إيقاف البحث التلقائي**\n\n"
        f"📊 **الإحصائيات النهائية:**\n"
        f"• اليوزرات المفحوصة: {checker.checked_count}\n"
        f"• اليوزرات المحفوظة: {saved_after}\n"
        f"• اليوزرات الجديدة: {new_saved}\n\n"
        "💾 لعرض اليوزرات: /saved\n"
        "▶️ للبدء مجدداً: /auto_start"
    )

async def saved(update, context):
    """عرض المحفوظات مع تصنيف اليوزرات القصيرة"""
    saved = checker.load_saved()
    
    if saved:
        # تحليل المحفوظات
        three_char = [u for u in saved if len(u) == 3]
        four_char = [u for u in saved if len(u) == 4]
        other = [u for u in saved if len(u) not in [3, 4]]
        
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
            msg += "\n"
        
        if other:
            msg += "📝 **يوزرات أخرى:**\n"
            for i, u in enumerate(other[:5], 1):
                msg += f"{i}. `@{u}`\n"
            msg += "\n"
        
        msg += f"📊 **الإحصائيات:**\n"
        msg += f"• إجمالي المحفوظات: {len(saved)}\n"
        msg += f"• يوزرات 3 أحرف: {len(three_char)} 🎯\n"
        msg += f"• يوزرات 4 أحرف: {len(four_char)} ⭐\n"
        msg += f"• يوزرات أخرى: {len(other)}"
        
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
    numbers_only = [u for u in saved if u.isdigit()]
    letters_only = [u for u in saved if u.isalpha()]
    
    msg = f"""📊 **إحصائيات متقدمة**

💾 **المحفوظات:**
• الإجمالي: {len(saved)} يوزر
• يوزرات 3 أحرف: {len(three_char)} 🎯
• يوزرات 4 أحرف: {len(four_char)} ⭐

🎯 **التفاصيل:**
• يوزرات أرقام فقط: {len(numbers_only)}
• يوزرات أحرف فقط: {len(letters_only)}
• يوزرات مختلطة: {len(saved) - len(numbers_only) - len(letters_only)}

⚡ **الأداء:**
• اليوزرات المفحوصة: {checker.checked_count}
• البحث التلقائي: {auto_status}

🚀 البوت مخصص لليوزرات القصيرة فقط!"""
    
    await update.message.reply_text(msg)

async def help_command(update, context):
    """رسالة المساعدة المخصصة"""
    help_text = """🆘 **مساعدة بوت اليوزرات القصيرة**

🎯 **الهدف:**
البحث عن يوزرات تيك توك نادرة مكونة من 3-4 أحرف/أرقام فقط

🔍 **كيف يعمل:**
1. يركز على اليوزرات القصيرة (3-4 أحرف)
2. يحفظ اليوزرات المتاحة تلقائياً
3. يرسل إشعارات فورية للإيجادات

⚡ **الأوامر:**
/quick - بحث سريع (10 يوزرات)
/auto_start - بحث تلقائي مستمر
/auto_stop - إيقاف البحث التلقائي
/saved - عرض المحفوظات مع التصنيف
/stats - إحصائيات متقدمة

💡 **نصيحة:** 
استخدم /auto_start واترك البوت يعمل في الخلفية!
سيخبرك فوراً باكتشاف أي يوزر نادر."""
    
    await update.message.reply_text(help_text)

def main():
    """الدالة الرئيسية"""
    try:
        print("🚀 بدء تشغيل بوت اليوزرات القصيرة...")
        print("🎯 مخصص للبحث عن يوزرات 3-4 أحرف فقط")
        
        # إنشاء التطبيق
        application = Application.builder().token(BOT_TOKEN).build()
        
        # إضافة جميع الأوامر
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("quick", quick_search))
        application.add_handler(CommandHandler("auto_start", auto_start))
        application.add_handler(CommandHandler("auto_stop", auto_stop))
        application.add_handler(CommandHandler("saved", saved))
        application.add_handler(CommandHandler("stats", stats))
        application.add_handler(CommandHandler("help", help_command))
        
        print("✅ البوت جاهز للتشغيل!")
        print("🎯 يركز على اليوزرات القصيرة (3-4 أحرف)")
        print("🤖 إرسل /start للبوت للبدء")
        
        # تشغيل البوت
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ فشل في تشغيل البوت: {e}")
        print(f"❌ الخطأ: {e}")

if __name__ == '__main__':
    main()
