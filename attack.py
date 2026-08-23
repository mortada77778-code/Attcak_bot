
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "I'm alive, Cedric!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
    


import discord
from discord.ext import commands, tasks
import random
import os
import json

# إعدادات البوت والصلاحيات
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# إعدادات المعركة السحرية
MAX_HP = 200          
current_hp = MAX_HP
DAMAGE_PER_HIT = 10
raid_active = False

# التوقيع الرسمي للصانع
AUTHOR_SIGNATURE = "\n\n_— تم الصناعة بواسطة سيدريك 🪄_"

# ملف حفظ البيانات لتفادي فقدانها عند إعادة تشغيل البوت
DATA_FILE = "hacker_data.json"

def load_data():
    """تحميل النقاط والمرضى من الملف الخارجي لضمان عدم ضياعها"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # تحويل المفاتيح إلى أرقام صحيح (IDs)
                scores = {int(k): v for k, v in data.get("scores", {}).items()}
                patients = set(int(pid) for pid in data.get("patients", []))
                return scores, patients
        except Exception:
            pass
    return {}, set()

def save_data():
    """حفظ البيانات فوراً في الملف الخارجي"""
    data = {
        "scores": player_scores,
        "patients": list(hospital_patients)
    }
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

# تحميل البيانات عند تشغيل السكربت
player_scores, hospital_patients = load_data()

def get_health_bar(hp):
    filled = hp // 20
    empty = 10 - filled
    return "🟥" * filled + "🟩" * empty

class VillageDefenseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="⚡ اقضي على أكلة الموت! (هجوم سحري)", style=discord.ButtonStyle.danger, custom_id="village_defense_btn")
    async def defense_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        global current_hp, raid_active
        
        await interaction.response.defer()
        
        user_id = interaction.user.id
        user_name = interaction.user.name

        # فحص لو الساحر مريض في مستشفى سانت مانجو
        if user_id in hospital_patients:
            await interaction.followup.send(f"🏥✨ يا أستاذ، أنت ترقد حالياً في مستشفى سانت مانجو لتلقي العلاج السحري! لا يمكنك المبارزة حتى يشفيك أحد زملائك بالأمر `!علاج`." + AUTHOR_SIGNATURE, ephemeral=True)
            return

        if not raid_active:
            await interaction.followup.send(f"🪄 أسوار هوجوورتس آمنة تماماً ولا يوجد خطر ظلامي يهددنا حالياً!" + AUTHOR_SIGNATURE, ephemeral=True)
            return

        # تسجيل الضربات سحرياً
        if user_id not in player_scores:
            player_scores[user_id] = {"name": user_name, "hits": 0}
        player_scores[user_id]["hits"] += 1
        player_scores[user_id]["name"] = user_name
        save_data() # حفظ البيانات فوراً

        if current_hp > 0:
            current_hp -= DAMAGE_PER_HIT  
            if current_hp < 0:
                current_hp = 0
            
            if current_hp > 0:
                health_bar = get_health_bar(current_hp)
                await interaction.message.edit(
                    content=f"⚡ **[ إنذار سحري أحمر: معركة ضارية عند أسوار هوجوورتس! ]** ⚡\n"
                            f"أعوان **Death Eaters** يتقدمون بظلامهم ويحاولون اقتحام قلعة السحرة!\n\n"
                            f"🖤 **طاقة زعيم الموت المهاجم:** `{current_hp}/{MAX_HP}`\n"
                            f"[{health_bar}]\n\n"
                            f"🪄 *استمروا في إلقاء التعاويذ! آخر تعويذة مدمرة وجهها البطل:* **{user_name}** (-10 ضرر سحري 🔥)"
                            f"{AUTHOR_SIGNATURE}"
                )
            else:
                raid_active = False
                
                # اختيار ساحر عشوائي وإرساله لمستشفى سانت مانجو نهاية المعركة
                hospital_msg = ""
                if player_scores:
                    all_fighters = list(player_scores.keys())
                    victim_id = random.choice(all_fighters)
                    hospital_patients.add(victim_id)
                    save_data() # حفظ البيانات فوراً
                    victim_name = player_scores[victim_id]["name"]
                    hospital_msg = f"\n\n🚑 **[ طوارئ مستشفى سانت مانجو ]**:\n✨ للأسف، تعرض البطل **{victim_name}** لعنة قوية أثناء المعركة وسقط مغشياً عليه! تم نقله فوراً إلى الطابق الرابع (قسم الإصابات السحرية). استخدموا أمر `!علاج @{victim_name}` لشفائه!"

                await interaction.message.edit(
                    content=f"🏆 **[ نصر أسطوري يخلده تاريخ هوجوورتس! ]** 🏆\n"
                            f"بفضل شجاعة سحرة القلعة وبسالة **{user_name}** ومن معه، تم دحر جيش الـ Death Eaters وطرد الظلام بعيداً! 🎉🛡️✨"
                            f"{hospital_msg}\n\n"
                            f"📊 *اكتب أمر `!صدارة` لمراجعة سجل الأبطال، أو `!مستشفى` لعرض المصابين!*"
                            f"{AUTHOR_SIGNATURE}"
                )
        else:
            await interaction.followup.send(f"⚡ المعركة انتهت وتم القضاء على أكلة الموت مسبقاً!" + AUTHOR_SIGNATURE, ephemeral=True)

@bot.event
async def on_ready():
    print(f"تم تسجيل الدخول بنجاح باسم الساحر: {bot.user}")
    bot.add_view(VillageDefenseView())
    scheduled_attack.start()

@bot.command(name="هجوم")
async def start_raid_command(ctx):
    global current_hp, raid_active
    current_hp = MAX_HP
    raid_active = True
    
    health_bar = get_health_bar(MAX_HP)
    await ctx.send(
        f"🚨 **[ خطر يلوح في أفق هوجوورتس! ]** 🚨\n"
        f"تجمع قتلة السحرة وجماعة **Death Eaters** في الأفق ومعهم طاقة مظلمة لتهشيم البوابات!\n\n"
        f"🖤 **طاقة زعيم الموت المهاجم:** `{current_hp}/{MAX_HP}`\n"
        f"[{health_bar}]\n\n"
        f"🪄 **يا أبناء هوجوورتس والأبطال، استعدوا للمبارزة واضغطوا على زر الدفاع أدناه بسرعة لحماية القلعة!**"
        f"{AUTHOR_SIGNATURE}",
        view=VillageDefenseView()
    )

# أمر علاج المريض بمستشفى سانت مانجو (متاح للجميع)
@bot.command(name="علاج")
async def cure_patient(ctx, member: discord.Member):
    if member.id in hospital_patients:
        hospital_patients.remove(member.id)
        save_data() # حفظ التحديث بعد الشفاء
        await ctx.send(
            f"🌿✨ **[ تعويذة شفاء ملكية من جناح المستشفى ]** ✨🌿\n\n"
            f"🪄 قام البطل **{ctx.author.name}** بالتلويح بعصاه السحرية واستخدام جرعة **'بيبر ووبل' (Pepperup Potion)** الفعالة للساحر **{member.name}**!\n"
            f"💨 (طلع دخان من أذنيه من قوة الجرعة!).. لكنه تعافى تماماً وعادت إليه طاقته السحرية.\n\n"
            f"🎉 **الحمد لله على السلامة يا بطل!** لقد خرجت من مستشفى سانت مانجو وأصبحت جاهزاً للعودة إلى قتال أكلة الموت! ⚔️🔥"
            f"{AUTHOR_SIGNATURE}"
        )
    else:
        await ctx.send(f"🔮 يا أستاذ، الساحر **{member.name}** ليس مريضاً في مستشفى سانت مانجو أساساً.. هو يتجول في ممرات هوجوورتس بكامل طاقته وسحره!" + AUTHOR_SIGNATURE)

@cure_patient.error
async def cure_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"⚠️ يا ريت تحدد الساحر المراد علاجه بشكل صحيح، مثلاً: `!علاج @اسم_الساحر`" + AUTHOR_SIGNATURE)

# أمر عرض قائمة المرضى في مستشفى سانت مانجو
@bot.command(name="مستشفى")
async def hospital_status(ctx):
    if not hospital_patients:
        await ctx.send(f"🏥 **[ مستشفى سانت مانجو ]**:\n✨ المستشفى هادئة تماماً ولا يوجد أي ساحر راقد في الأسرّة حالياً.. الجميع في قمة لياقتهم السحرية!" + AUTHOR_SIGNATURE)
        return
    
    patients_list = "🏥 **[ سجلات مرضى الطابق الرابع - سانت مانجو ]** 🏥\n\n"
    for pid in hospital_patients:
        p_name = player_scores.get(pid, {}).get("name", "ساحر مجهول")
        patients_list += f"🛏️ الساحر **{p_name}** (يرقد تحت تأثير تعويذة علاجية)\n"
    
    patients_list += "\n🪄 *استخدموا أمر `!علاج @اسم_الساحر` لتقديم الجرعات السحرية لهم!*"
    patients_list += AUTHOR_SIGNATURE
    await ctx.send(patients_list)

# لوحة شرف أبطال هوجوورتس
@bot.command(name="صدارة")
async def leaderboard_command(ctx):
    if not player_scores:
        await ctx.send(f"📊 **لوحة شرف هوجوورتس فارغة حالياً! مافي زول شارك في المبارزات لسه.**" + AUTHOR_SIGNATURE)
        return

    sorted_players = sorted(player_scores.values(), key=lambda x: x["hits"], reverse=True)
    
    table_lines = []
    table_lines.append(f"{'المرتبة':<8} | {'اسم الساحر':<15} | {'التعاويذ':<8} | {'الضرر':<6}")
    table_lines.append("-" * 45)
    
    medals = ["🥇 الأول", "🥈 الثاني", "🥉 الثالث", " 4     ", " 5     ", " 6     ", " 7     ", " 8     ", " 9     ", " 10    "]
    for i, player in enumerate(sorted_players[:10]):
        rank = medals[i]
        name = player["name"][:14].ljust(15)
        hits = str(player["hits"]).ljust(8)
        damage = str(player["hits"] * DAMAGE_PER_HIT).ljust(6)
        
        table_lines.append(f"{rank:<8} | {name} | {hits} | {damage}")
    
    formatted_table = "```text\n" + "\n".join(table_lines) + "\n```"
    
    await ctx.send(
        f"🏆 **[ سجل شرف أبطال هوجوورتس - صدارة المدافعين ]** 🏆\n"
        f"{formatted_table}\n"
        f"🎁 *استمروا في حماية القلعة لرفع نقاطكم وتصدر قمة السحرة!*"
        f"{AUTHOR_SIGNATURE}"
    )

@tasks.loop(hours=2)
async def scheduled_attack():
    global current_hp, raid_active
    channel_id = 1540623521774960682  
    channel = bot.get_channel(channel_id)
    
    if channel:
        current_hp = MAX_HP
        raid_active = True
        health_bar = get_health_bar(MAX_HP)
        
        hospital_msg = ""
        if player_scores:
            all_fighters = list(player_scores.keys())
            victim_id = random.choice(all_fighters)
            hospital_patients.add(victim_id)
            save_data() # حفظ البيانات تلقائياً
            victim_name = player_scores[victim_id]["name"]
            hospital_msg = f"\n\n🚑 **[ طوارئ المعركة الفائته ]**:\n✨ أُصيب الساحر **{victim_name}** ونُقل لمستشفى سانت مانجو! عالجوه بـ `!علاج @{victim_name}`."

        await channel.send(
            f"🚨 **[ هجوم ظلامي مباغت على هوجوورتس! ]** 🚨\n"
            f"تجمع قتلة السحرة وجماعة **Death Eaters** في الأفق ومعهما طاقة مظلمة لتهشيم البوابات!\n\n"
            f"🖤 **طاقة زعيم الموت المهاجم:** `{current_hp}/{MAX_HP}`\n"
            f"[{health_bar}]"
            f"{hospital_msg}\n\n"
            f"🪄 **يا أبناء هوجوورتس، استعدوا للمبارزة واضغطوا على زر الدفاع أدناه بسرعة لحماية القلعة!**"
            f"{AUTHOR_SIGNATURE}",
            view=VillageDefenseView()
        )
keep_alive()
# تشغيل البوت باستخدام متغير البيئة في رندر
bot.run(os.getenv("BOT_TOKEN"))



