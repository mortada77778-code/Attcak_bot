import discord
from discord.ext import commands
import random
import os

# إعدادات الصلاحيات (Intents)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# تعريف البوت مع بادئة الأوامر !
bot = commands.Bot(command_prefix="!", intents=intents)

# توقيع المطور
AUTHOR_SIGNATURE = "\n\n_— تم الصناعة بواسطة سيدريك 🪄_"

@bot.event
async def on_ready():
    print(f"تم تسجيل الدخول بنجاح لبوت الهجوم باسم: {bot.user}")

# ----------------- أمر الهجوم السحري (!هجوم) ----------------- #
@bot.command(name="هجوم")
async def attack_member(ctx, member: discord.Member):
    attacks = [
        f"⚡ أطلق تعويذة **الصاعقة المدمرة** على الساحر {member.mention}!",
        f"🔥 رمى كرة من **النيران التنينية** مباشرة نحو {member.mention}!",
        f"🧊 جَمّد أطراف الساحر {member.mention} بتعويذة **الصقيع الجليدي**!",
        f"🌪️ أحدث عاصفة من **الرياح العاتية** رفعت {member.mention} في الهواء!",
        f"✨ باغته بلعنة **الارتباك السحري** وجعل {member.mention} يترنح مكانه!"
    ]
    chosen_attack = random.choice(attacks)
    await ctx.send(
        f"⚔️ **[ معركة السحرة في هوجوورتس ]** ⚔️\n"
        f"المقاتل الشجاع **{ctx.author.name}** شلع البوابات وقام بالهجوم!\n\n"
        f"{chosen_attack}\n\n"
        f"💥 **استعد للدفاع يا {member.mention}!**"
        f"{AUTHOR_SIGNATURE}"
    )

# ----------------- أمر معلومات البوت (!about) ----------------- #
@bot.command(name="about")
async def about_bot(ctx):
    await ctx.send(
        "🔮 **[ سجلات معهد هوجوورتس للسحرة ]** 🔮\n"
        "أنا بوت الهجوم السحري، مخصص لإشعال الحماس وإدارة المعارك في السيرفر بكل قوة!\n"
        f"🛡️ الحالة: شغال 24 ساعة بدون توقف.\n"
        f"{AUTHOR_SIGNATURE}"
    )

# ----------------- أمر قائمة الأوامر (!اوامر) ----------------- #
@bot.command(name="اوامر")
async def help_menu(ctx):
    await ctx.send(
        "📜 **[ تعاويذ وأوامر بوت الهجوم المتاحة ]** 📜\n\n"
        "⚡ `!هجوم @الساحر` - لشن هجوم سحري عشوائي ومباغت على أي عضو!\n"
        "ℹ️ `!about` - لمعرفة قصة البوت ومعلومات عنه.\n"
        "❓ `!اوامر` - لعرض هذه القائمة السحرية.\n\n"
        f"جاهزون دائماً للمعارك يا أبطال!{AUTHOR_SIGNATURE}"
    )

# تشغيل البوت باستخدام توكن البيئة
bot.run(os.getenv("BOT_TOKEN"))
