import discord
from discord.ext import commands
import json
import platform
import psutil

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix='/', intents=intents)

# Load data from JSON files
def load_data():
    try:
        with open('log-data.json', 'r') as f:
            log_data = json.load(f)
    except FileNotFoundError:
        log_data = {}

    try:
        with open('databot.json', 'r') as f:
            bot_data = json.load(f)
    except FileNotFoundError:
        bot_data = {}

    return log_data, bot_data

log_data, bot_data = load_data()
log_channel_id = log_data.get('log_channel_id')
update_channel_id = log_data.get('update_channel_id')
update_role_id = log_data.get('update_role_id')

# Save data to JSON files
def save_data():
    with open('log-data.json', 'w') as f:
        json.dump({'log_channel_id': log_channel_id, 'update_channel_id': update_channel_id, 'update_role_id': update_role_id}, f)

    with open('databot.json', 'w') as f:
        json.dump(bot_data, f)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message_edit(before, after):
    if log_channel_id:
        embed = discord.Embed(color=discord.Color.green(), description=f'A message was modified\n**User ID:** {after.author.id}\n**Message:** {after.content}')
        embed.set_footer(text='github.com/mihai14launcher')
        channel = bot.get_channel(log_channel_id)
        await channel.send(embed=embed)

@bot.event
async def on_message_delete(message):
    if log_channel_id:
        embed = discord.Embed(color=discord.Color.red(), description=f'A message was deleted\n**User ID:** {message.author.id}\n**Message:** {message.content}')
        embed.set_footer(text='github.com/mihai14launcher')
        channel = bot.get_channel(log_channel_id)
        await channel.send(embed=embed)

@bot.event
async def on_voice_state_update(member, before, after):
    if log_channel_id:
        if before.channel is None and after.channel is not None:
            embed = discord.Embed(color=discord.Color.lime(), description=f'A user joined the channel\n**User ID:** {member.id}\n**Channel Name:** {after.channel.name}')
            embed.set_footer(text='github.com/mihai14launcher')
        elif before.channel is not None and after.channel is None:
            embed = discord.Embed(color=discord.Color.lime(), description=f'A user left the channel\n**User ID:** {member.id}\n**Channel Name:** {before.channel.name}')
            embed.set_footer(text='github.com/mihai14launcher')
        else:
            return
        channel = bot.get_channel(log_channel_id)
        await channel.send(embed=embed)

@bot.event
async def on_member_join(member):
    if log_channel_id:
        embed = discord.Embed(color=discord.Color.yellow(), description=f'A user joined the server\n**User ID:** {member.id}\n**Server Name:** {member.guild.name}')
        embed.set_footer(text='github.com/mihai14launcher')
        channel = bot.get_channel(log_channel_id)
        await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    if log_channel_id:
        embed = discord.Embed(color=discord.Color.dark_gray(), description=f'A user left the server\n**User ID:** {member.id}\n**Server Name:** {member.guild.name}')
        embed.set_footer(text='github.com/mihai14launcher')
        channel = bot.get_channel(log_channel_id)
        await channel.send(embed=embed)

@bot.event
async def on_message(message):
    if update_channel_id and message.channel.id == update_channel_id:
        update_channel = bot.get_channel(update_channel_id)
        role = message.guild.get_role(update_role_id)
        embed = discord.Embed(color=discord.Color.blue(), description=message.content)
        embed.set_footer(text='github.com/mihai14launcher')
        await update_channel.send(content=role.mention, embed=embed)
    await bot.process_commands(message)

@bot.command()
async def setlog(ctx, channel: discord.TextChannel):
    global log_channel_id
    log_channel_id = channel.id
    save_data()
    await ctx.send(f'Log channel set to {channel.mention}')

@bot.command()
async def stoplog(ctx):
    global log_channel_id
    log_channel_id = None
    save_data()
    await ctx.send('Logging stopped')

@bot.command()
async def updates(ctx, channel: discord.TextChannel, role: discord.Role):
    global update_channel_id, update_role_id
    update_channel_id = channel.id
    update_role_id = role.id
    save_data()
    await ctx.send(f'Update notifications set to {channel.mention} for role {role.mention}')

@bot.command()
async def about(ctx):
    embed = discord.Embed(color=discord.Color.yellow(), title=f'About {bot.user.name}')
    embed.add_field(name='💻 System', value=platform.system(), inline=False)
    embed.add_field(name='⚙️ Ram', value=f'{psutil.virtual_memory().used // (1024 ** 2)}MB | {psutil.virtual_memory().total // (1024 ** 2)}MB', inline=False)
    embed.add_field(name='🔨 Cpu', value=f'{psutil.cpu_percent()}% | {psutil.cpu_count(logical=True)} cores', inline=False)
    embed.add_field(name='✅ Manufacter', value='Unknown', inline=False)  # Replace with actual value if available
    embed.add_field(name='📑 Storage', value=f'{psutil.disk_usage("/").used // (1024 ** 3)}GB | {psutil.disk_usage("/").total // (1024 ** 3)}GB', inline=False)
    embed.add_field(name='🤖 Version', value='0.1 A', inline=False)
    embed.set_footer(text='github.com/mihai14launcher')
    await ctx.send(embed=embed)

bot.run('YOUR_BOT_TOKEN')
