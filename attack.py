import discord
from discord.ext import commands
import random
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

AUTHOR_SIGNATURE = "\n\n_— تم الصناعة بواسطة سيدريك 🪄_"

@bot.event
async def on_ready():
    print(f"تم تسجيل الدخول بنجاح لبوت الهجوم باسم: {bot.user}")

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

@bot.command(name="about")
async def about_bot(ctx):
    await ctx.send("🔮 أنا بوت الهجوم السحري، جاهز للمعارك!\n" + AUTHOR_SIGNATURE)

@bot.command(name="help")
async def help_menu(ctx):
    await ctx.send("📜 الأوامر: `!هجوم @الشخص`, `!about`\n" + AUTHOR_SIGNATURE)

bot.run(os.getenv("BOT_TOKEN"))
