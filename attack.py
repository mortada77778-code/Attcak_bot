import discord
from discord.ext import commands
import random
import os
from flask import Flask
from threading import Thread

# ----------------- إعدادات سيرفر الويب الخفي (لبقاء البوت صاحي 24 ساعة) ----------------- #
app = Flask('')

@app.route('/')
def home():
    return "I am alive! بوت الهجوم شغال وصاحي 24 ساعة 🚀"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ----------------- إعدادات البوت الأساسية ----------------- #
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# التوقيع الرسمي للصانع
AUTHOR_SIGNATURE = "\n\n_— تم الصناعة بواسطة سيدريك 🪄_"

@bot.event
async def on_ready():
    print(f"تم تسجيل الدخول بنجاح لبوت الهجوم باسم: {bot.user}")

# ----------------- أمر الهجوم السحري ----------------- #
@bot.command(name="هجوم")
async def attack_member(ctx, member: discord.Member):
    # قائمة بأساليب الهجوم السحري
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

@attack_member.error
async def attack_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            f"⚠️ يا ريت تحدد الساحر المراد مهاجمته بشكل صحيح، مثلاً:\n`!هجوم @اسم_الساحر`"
            + AUTHOR_SIGNATURE
        )

# ----------------- تشغيل السيرفر الخفي والبوت معاً ----------------- #
if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv("BOT_TOKEN"))
