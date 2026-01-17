import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import aiohttp
import certifi
import ssl
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fix for macOS SSL certificate issue
if os.name == 'posix':
    import ssl
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

# Configuration
TOKEN = os.getenv('DISCORD_TOKEN')
CONFIG_FILE = 'config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

# Set up intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class WelcomeBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        # Sync slash commands
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}")

bot = WelcomeBot()

def find_channel(guild, keywords):
    """Search for a channel that matches any of the keywords, prioritizing exact matches."""
    # First pass: look for exact matches
    for channel in guild.text_channels:
        name = channel.name.lower()
        if any(key == name for key in keywords):
            return channel
    
    # Second pass: look for partial matches
    for channel in guild.text_channels:
        name = channel.name.lower()
        if any(key in name for key in keywords):
            return channel
    return None

@bot.event
async def on_ready():
    print(f'--- Bot is online ---')
    print(f'Logged in as: {bot.user.name}')
    print(f'----------------------')
    # Force sync on ready to ensure slash commands show up
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.tree.command(name="set_welcome_channel", description="Sets the channel where welcome messages will be sent")
@app_commands.describe(channel="The channel to send welcome messages in")
async def set_welcome_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    config = load_config()
    config[str(interaction.guild_id)] = channel.id
    save_config(config)
    await interaction.response.send_message(f"Welcome channel has been set to {channel.mention}", ephemeral=True)

@bot.event
async def on_member_join(member):
    guild = member.guild
    config = load_config()
    
    # Get saved welcome channel or try to find one named 'welcome'
    welcome_channel_id = config.get(str(guild.id))
    welcome_channel = guild.get_channel(welcome_channel_id) if welcome_channel_id else None
    
    if not welcome_channel:
        welcome_channel = find_channel(guild, ['welcome', 'joins', 'greet'])

    # Dynamically search for other channels
    rules_channel = find_channel(guild, ['rules', 'rule', 'regulation', '📜'])
    announcements_channel = find_channel(guild, ['announcement', 'news', 'broadcast', '📢'])
    general_chat = find_channel(guild, ['general', 'main', '🗨'])

    # Find the custom emoji by name (try with and without colons)
    emoji_1 = ":emoji_1:" 
    # Discord emoji names in code don't have colons, but users often think they do
    target_emoji_name = "emoji_1"
    custom_emoji = discord.utils.get(guild.emojis, name=target_emoji_name)
    
    if custom_emoji:
        emoji_1 = str(custom_emoji)
    
    # Get owner display name
    owner_name = "the"
    if guild.owner:
        owner_name = guild.owner.display_name
    elif guild.owner_id:
        try:
            owner = await guild.fetch_member(guild.owner_id)
            if owner:
                owner_name = owner.display_name
        except:
            pass

    # Create Embed for a bigger PFP and better look
    embed = discord.Embed(
        title=f"Welcome to {guild.name} Server",
        description=f"We hope you enjoy your time here !!!!\n\n"
                    f"{emoji_1}  {rules_channel.mention if rules_channel else '⁠📃｜rules'}\n"
                    f"{emoji_1}  {announcements_channel.mention if announcements_channel else '⁠📢｜announcements'}\n"
                    f"{emoji_1}  {general_chat.mention if general_chat else '⁠🗨｜general-chat'}",
        color=discord.Color.blue()
    )
    
    # Set the profile picture as the large image
    if member.display_avatar:
        embed.set_image(url=member.display_avatar.url)
    
    # Add the welcome to owner message below the image
    embed.set_footer(text=f"Welcome to {owner_name}'s Server!!!")

    if welcome_channel:
        try:
            # Send the member ping above the embed
            await welcome_channel.send(content=member.mention, embed=embed)
        except Exception as e:
            print(f"Failed to send welcome message: {e}")

if __name__ == "__main__":
    if TOKEN:
        # Create a custom SSL context that bypasses verification
        # This is needed for some macOS environments with broken certificate chains
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Patch aiohttp.TCPConnector to use our SSL context by default
        import aiohttp
        original_tcp_init = aiohttp.TCPConnector.__init__
        def patched_tcp_init(self, *args, **kwargs):
            if 'ssl' not in kwargs:
                kwargs['ssl'] = ssl_context
            original_tcp_init(self, *args, **kwargs)
        aiohttp.TCPConnector.__init__ = patched_tcp_init
        
        bot.run(TOKEN)
    else:
        print("ERROR: DISCORD_TOKEN not found in .env file.")

