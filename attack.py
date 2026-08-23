import discord
from discord.ext import commands, tasks
import random
import os

# إعدادات البوت والصلاحيات
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# إعدادات المعركة السحرية
MAX_HP = 200          
current_hp = MAX_HP
DAMAGE_PER_HIT = 10
raid_active = False

# قوائم اللاعبين ومستشفى سانت مانجو السحرية
player_scores = {}  # {user_id: {"name": "اسم", "hits": عدد الضربات}}
hospital_patients = set()  # مجموعة IDs المرضى في المستشفى حالياً

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
            await interaction.followup.send("🏥✨ يا أستاذ، أنت ترقد حالياً في مستشفى سانت مانجو لتلقي العلاج السحري! لا يمكنك المبارزة حتى يشفيك أحد زملائك بالأمر `!علاج`.", ephemeral=True)
            return

        if not raid_active:
            await interaction.followup.send("🪄 أسوار هوجوورتس آمنة تماماً ولا يوجد خطر ظلامي يهددنا حالياً!", ephemeral=True)
            return

        # تسجيل الضربات سحرياً
        if user_id not in player_scores:
            player_scores[user_id] = {"name": user_name, "hits": 0}
        player_scores[user_id]["hits"] += 1
        player_scores[user_id]["name"] = user_name

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
                )
            else:
                raid_active = False
                
                # اختيار ساحر عشوائي وإرساله لمستشفى سانت مانجو نهاية المعركة
                hospital_msg = ""
                if player_scores:
                    all_fighters = list(player_scores.keys())
                    victim_id = random.choice(all_fighters)
                    hospital_patients.add(victim_id)
                    victim_name = player_scores[victim_id]["name"]
                    hospital_msg = f"\n\n🚑 **[ طوارئ مستشفى سانت مانجو ]**:\n✨ للأسف، تعرض البطل **{victim_name}** لعنة قوية أثناء المعركة وسقط مغشياً عليه! تم نقله فوراً إلى الطابق الرابع (قسم الإصابات السحرية). استخدموا أمر `!علاج @{victim_name}` لشفائه!"

                await interaction.message.edit(
                    content=f"🏆 **[ نصر أسطوري يخلده تاريخ هوجوورتس! ]** 🏆\n"
                            f"بفضل شجاعة سحرة القلعة وبسالة **{user_name}** ومن معه، تم دحر جيش الـ Death Eaters وطرد الظلام بعيداً! 🎉🛡️✨"
                            f"{hospital_msg}\n\n"
                            f"📊 *اكتب أمر `!صدارة` لمراجعة سجل الأبطال، أو `!مستشفى` لعرض المصابين!*"
                )
        else:
            await interaction.followup.send("⚡ المعركة انتهت وتم القضاء على أكلة الموت مسبقاً!", ephemeral=True)

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
        f"🪄 **يا أبناء هوجوورتس والأبطال، استعدوا للمبارزة واضغطوا على زر الدفاع أدناه بسرعة لحماية القلعة!**",
        view=VillageDefenseView()
    )

# أمر علاج المريض بمستشفى سانت مانجو (متاح للجميع)
@bot.command(name="علاج")
async def cure_patient(ctx, member: discord.Member):
    if member.id in hospital_patients:
        hospital_patients.remove(member.id)
        await ctx.send(
            f"🌿✨ **[ تعويذة شفاء ملكية من جناح المستشفى ]** ✨🌿\n\n"
            f"🪄 قام البطل **{ctx.author.name}**تلويح عصاه السحرية واستخدام جرعة **'بيبر ووبل' (Pepperup Potion)** الفعالة للساحر **{member.name}**!\n"
            f"💨 (طلع دخان من أذنيه من قوة الجرعة!).. لكنه تعافى تماماً وعادت إليه طاقته السحرية.\n\n"
            f"🎉 **الحمد لله على السلامة يا بطل!** لقد خرجت من مستشفى سانت مانجو وأصبحت جاهزاً للعودة إلى قتال أكلة الموت! ⚔️🔥"
        )
    else:
        await ctx.send(f"🔮 يا أستاذ، الساحر **{member.name}** ليس مريضاً في مستشفى سانت مانجو أساساً.. هو يتجول في ممرات هوجوورتس بكامل طاقته وسحره!")

@cure_patient.error
async def cure_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ يا ريت تحدد الساحر المراد علاجه بشكل صحيح، مثلاً: `!علاج @اسم_الساحر`")

# أمر عرض قائمة المرضى في مستشفى سانت مانجو
@bot.command(name="مستشفى")
async def hospital_status(ctx):
    if not hospital_patients:
        await ctx.send("🏥 **[ مستشفى سانت مانجو ]**:\n✨ المستشفى هادئة تماماً ولا يوجد أي ساحر راقد في الأسرّة حالياً.. الجميع في قمة لياقتهم السحرية!")
        return
    
    patients_list = "🏥 **[ سجلات مرضى الطابق الرابع - سانت مانجو ]** 🏥\n\n"
    for pid in hospital_patients:
        p_name = player_scores.get(pid, {}).get("name", "ساحر مجهول")
        patients_list += f"🛏️ الساحر **{p_name}** (يرقد تحت تأثير تعويذة علاجية)\n"
    
    patients_list += "\n🪄 *استخدموا أمر `!علاج @اسم_الساحر` لتقديم الجرعات السحرية لهم!*"
    await ctx.send(patients_list)

# لوحة شرف أبطال هوجوورتس
@bot.command(name="صدارة")
async def leaderboard_command(ctx):
    if not player_scores:
        await ctx.send("📊 **لوحة شرف هوجوورتس فارغة حالياً! مافي زول شارك في المبارزات لسه.**")
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
            victim_name = player_scores[victim_id]["name"]
            hospital_msg = f"\n\n🚑 **[ طوارئ المعركة الفائته ]**:\n✨ أُصيب الساحر **{victim_name}** ونُقل لمستشفى سانت مانجو! عالجوه بـ `!علاج @{victim_name}`."

        await channel.send(
            f"🚨 **[ هجوم ظلامي مباغت على هوجوورتس! ]** 🚨\n"
            f"تجمع قتلة السحرة وجماعة **Death Eaters** في الأفق ومعهما طاقة مظلمة لتهشيم البوابات!\n\n"
            f"🖤 **طاقة زعيم الموت المهاجم:** `{current_hp}/{MAX_HP}`\n"
            f"[{health_bar}]"
            f"{hospital_msg}\n\n"
            f"🪄 **يا أبناء هوجوورتس، استعدوا للمبارزة واضغطوا على زر الدفاع أدناه بسرعة لحماية القلعة!**",
            view=VillageDefenseView()
        )

# تشغيل البوت باستخدام متغير البيئة في رندر
bot.run(os.getenv("BOT_TOKEN"))
        else:
            await interaction.followup.send("⚡ المعركة انتهت وتم القضاء على الخطر مسبقاً!", ephemeral=True)

@bot.event
async def on_ready():
    print(f"تم تسجيل الدخول بنجاح باسم: {bot.user}")
    bot.add_view(VillageDefenseView())
    scheduled_attack.start()

@bot.command(name="هجوم")
async def start_raid_command(ctx):
    global current_hp, raid_active
    current_hp = MAX_HP
    raid_active = True
    
    health_bar = get_health_bar(MAX_HP)
    await ctx.send(
        f"🚨 **[ غارة مرعبة تهدد القرية! ]** 🚨\n"
        f"تجمع قتلة السحرة وجماعة **Death Eaters** في الأفق ومعهما طاقة مظلمة لتهشيم البوابات!\n\n"
        f"🖤 **صحة زعيم الموت المهاجم:** `{current_hp}/{MAX_HP}`\n"
        f"[{health_bar}]\n\n"
        f"🛡️ **يا أهالي القرية والأبطال، استعدوا للمعركة واضغطوا على زر الدفاع أدناه بسرعة لانقاذ الوطن!**",
        view=VillageDefenseView()
    )

# أمر علاج المريض بواسطة رول مدير المستشفى مع رسالة فخمة وحماسية
@bot.command(name="علاج")
@commands.has_role("اسم_رول_مدير_المستشفى_هنا") # استبدل الاسم برول مدير المستشفى في سيرفرك
async def cure_patient(ctx, member: discord.Member):
    if member.id in hospital_patients:
        hospital_patients.remove(member.id)
        await ctx.send(
            f"🏥✨ **[ تقرير المستشفى الطبي العاجل ]** ✨🏥\n\n"
            f"🩺 بفضل مهارة وحنكة إدارة المستشفى، تم بححمد الله إجراء الإسعافات اللازمة للبطل **{member.name}**.\n"
            f"💉 تلقى الجرعات السحرية وعاد إليه نشاطه الكامل!\n\n"
            f"🎉 **مبروك يا بطل!** لقد غادرت المستشفى الآن وأصبحت بكامل صحتك وقوتك.. استعد للعودة إلى ساحة المعركة وسحق أكلة الموت! ⚔️🔥"
        )
    else:
        await ctx.send(f"ℹ️ يا وحش، البطل **{member.name}** ليس مريضاً في المستشفى أساساً.. هو بيجول في الشوارع وبكامل طاقته!")

@cure_patient.error
async def cure_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("⛔ عذراً يا غالي، أمر `!علاج` مخصص حصرياً لأصحاب رول **مدير المستشفى** فقط!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ يا ريت تحدد البطل المراد علاجه بشكل صحيح، مثلاً: `!علاج @اسم_الشخص`")

# أمر عرض قائمة المرضى في المستشفى
@bot.command(name="مستشفى")
async def hospital_status(ctx):
    if not hospital_patients:
        await ctx.send("🏥 **قرية سليمة وخالية من الإصابات:** المستشفى فارغة تماماً ولا يوجد أي مرضى حالياً!")
        return
    
    patients_list = "🏥 **[ قائمة مرضى المستشفى الحاليين ]** 🏥\n\n"
    for pid in hospital_patients:
        p_name = player_scores.get(pid, {}).get("name", "مقاتل مجهول")
        patients_list += f"🛌 البطل **{p_name}** (يرقد لتلقي العلاج)\n"
    
    patients_list += "\n🩺 *على مدير المستشفى استخدام أمر `!علاج @الإسم` لشفائهم!*"
    await ctx.send(patients_list)

# لوحة الصدارة بجدول مرتب ونظيف
@bot.command(name="صدارة")
async def leaderboard_command(ctx):
    if not player_scores:
        await ctx.send("📊 **لوحة الصدارة فارغة حالياً! مافي زول شارك في المعارك لسه.**")
        return

    sorted_players = sorted(player_scores.values(), key=lambda x: x["hits"], reverse=True)
    
    table_lines = []
    table_lines.append(f"{'المرتبة':<8} | {'اسم البطل':<15} | {'الضربات':<8} | {'الضرر':<6}")
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
        f"🏆 **[ لوحة شرف أبطال القرية - صدارة المدافعين ]** 🏆\n"
        f"{formatted_table}\n"
        f"🎁 *استمروا في الدفاع عن القرية لزيادة نقاطكم وتصدر القمة!*"
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
            victim_name = player_scores[victim_id]["name"]
            hospital_msg = f"\n\n🚑 **طوارئ الغارة السابقة:** أُصيب البطل **{victim_name}** ونُقل للمستشفى! على مدير المستشفى علاجه بـ `!علاج @{victim_name}`."

        await channel.send(
            f"🚨 **[ غارة مرعبة تهدد القرية! ]** 🚨\n"
            f"تجمع قتلة السحرة وجماعة **Death Eaters** في الأفق ومعهما طاقة مظلمة لتهشيم البوابات!\n\n"
            f"🖤 **صحة زعيم الموت المهاجم:** `{current_hp}/{MAX_HP}`\n"
            f"[{health_bar}]"
            f"{hospital_msg}\n\n"
            f"🛡️ **يا أهالي القرية والأبطال، استعدوا للمعركة واضغطوا على زر الدفاع أدناه بسرعة لانقاذ الوطن!**",
            view=VillageDefenseView()
        )



bot.run(os.getenv("BOT_TOKEN"))

@bot.command(name="سيدريك")
async def made_by_cedric(ctx):
    await ctx.send("تم الصناعة بواسطة سيدريك")

