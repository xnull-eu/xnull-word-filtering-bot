import discord
from discord import app_commands
from discord.ext import commands
from fuzzywuzzy import fuzz

# Bot configuration
SIMILARITY_THRESHOLD = 50  # Default value

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)  # Prefix won't be used but is required

# List of words to filter globally
filter_words = []
# Dictionary for user-specific filters
user_filters = {}

print("=== XNull Word Filtering Bot ===")
print("\nVisit https://www.xnull.eu for more projects and tools!")

print("\nTo get your bot token:")
print("1. Go to https://discord.com/developers/applications")
print("2. Click on your application (or create a new one)")
print("3. Go to the 'Bot' section")
print("4. Click 'Reset Token' or 'Copy' under the token section")
print("\nMake sure to keep your token secret and never share it with anyone!")
print("------------------------")

print(f"SIMILARITY_THRESHOLD is set to {SIMILARITY_THRESHOLD}. It is recommended to keep it at this value for optimal filtering.")

@bot.event
async def on_ready():
    # Generate and display invite link with required permissions
    permissions = discord.Permissions()
    permissions.read_messages = True        # Read Messages/View Channels
    permissions.send_messages = True        # Send Messages
    permissions.manage_messages = True      # Delete Messages
    permissions.read_message_history = True # Read Message History
    permissions.use_application_commands = True  # Use Application Commands

    invite_link = discord.utils.oauth_url(
        bot.user.id,
        permissions=permissions,
        scopes=["bot", "applications.commands"]
    )

    # Set activity and print ready message
    activity = discord.Game(name="/fwords to see filtered words") if filter_words else discord.Game(name="No filters set")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    
    print("\n=== Bot is ready! ===")
    print(f"\nInvite the bot to your server using this link:")
    print(f"\n{invite_link}\n")
    print("=" * 20)
    
    print(f'Logged in as {bot.user}')
    print("Initial global filter words:", ', '.join(filter_words) if filter_words else "None")
    
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    message_content_lower = message.content.lower()
    message_words = message_content_lower.split()

    # Check global filter words
    for word in filter_words:
        word_lower = word.lower()
        if word_lower in message_content_lower:
            await message.delete()
            break
        if SIMILARITY_THRESHOLD > 0:
            for msg_word in message_words:
                if fuzz.ratio(msg_word, word_lower) >= SIMILARITY_THRESHOLD:
                    await message.delete()
                    return

    # Check user-specific filter words
    user_specific_words = user_filters.get(message.author.id, [])
    for word in user_specific_words:
        word_lower = word.lower()
        if word_lower in message_content_lower:
            await message.delete()
            break
        if SIMILARITY_THRESHOLD > 0:
            for msg_word in message_words:
                if fuzz.ratio(msg_word, word_lower) >= SIMILARITY_THRESHOLD:
                    await message.delete()
                    return

@bot.tree.command(name="filter", description="Sets global filter words (Admin only)")
@app_commands.describe(words="Words to filter, separated by commas")
async def filter(interaction: discord.Interaction, words: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You need administrator permissions to use this command.", ephemeral=True)
        return
        
    global filter_words
    filter_words = [word.strip() for word in words.split(',')]
    activity = discord.Game(name="/fwords to see filtered words") if filter_words else discord.Game(name="No filters set")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    await interaction.response.send_message(f"Global filter words updated to: {', '.join(filter_words)}")

@bot.tree.command(name="ufilter", description="Sets filter words for a specific user (Admin only)")
@app_commands.describe(user="User to set filters for", words="Words to filter, separated by commas")
async def ufilter(interaction: discord.Interaction, user: discord.Member, words: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You need administrator permissions to use this command.", ephemeral=True)
        return
        
    user_filters[user.id] = [word.strip() for word in words.split(',')]
    await interaction.response.send_message(f"Custom filter words for {user.mention} updated to: {', '.join(user_filters[user.id])}")

@bot.tree.command(name="fwords", description="Displays the global filter words")
async def fwords(interaction: discord.Interaction):
    if filter_words:
        message = f"Global filter words: {', '.join(filter_words)}"
    else:
        message = "No global filter words set."
    await interaction.response.send_message(message)

@bot.tree.command(name="uwords", description="Displays filter words for users (Admin only)")
@app_commands.describe(user="Optional: Specific user to check filters for")
async def uwords(interaction: discord.Interaction, user: discord.Member = None):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You need administrator permissions to use this command.", ephemeral=True)
        return

    if user:
        user_words = user_filters.get(user.id, [])
        if user_words:
            message = f"Filter words for {user.mention}: {', '.join(user_words)}"
        else:
            message = f"No filter words set for {user.mention}."
    else:
        if user_filters:
            message = "User-specific filters:\n"
            user_filter_messages = []
            for user_id, words in user_filters.items():
                user = await bot.fetch_user(user_id)
                user_filter_messages.append(f"{user.mention}: {', '.join(words)}" if words else f"{user.mention}: No words set")
            message += "\n".join(user_filter_messages)
        else:
            message = "No user-specific filter words set."

    await interaction.response.send_message(message)

@bot.tree.command(name="reset", description="Clears all global filter words (Admin only)")
async def reset(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You need administrator permissions to use this command.", ephemeral=True)
        return
        
    global filter_words
    filter_words.clear()
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="No filters set"))
    await interaction.response.send_message("Global filter words have been reset.")

@bot.tree.command(name="ureset", description="Clears filters for specific users or all users (Admin only)")
@app_commands.describe(users="Optional: Users to reset filters for (leave empty for all users)")
async def ureset(interaction: discord.Interaction, users: str = None):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You need administrator permissions to use this command.", ephemeral=True)
        return
    
    if users:
        # Get all mentioned users from the command
        mentioned_users = []
        for user_id in [int(x) for x in users.replace('<@', '').replace('>', '').split()]:
            try:
                user = await bot.fetch_user(user_id)
                if user.id in user_filters:
                    del user_filters[user.id]
                    mentioned_users.append(user)
            except discord.NotFound:
                continue
        
        if mentioned_users:
            user_mentions = ', '.join(user.mention for user in mentioned_users)
            await interaction.response.send_message(f"Filter words for the specified users ({user_mentions}) have been reset.")
        else:
            await interaction.response.send_message("No valid users found to reset filters for.")
    else:
        user_filters.clear()
        await interaction.response.send_message("All user-specific filter words have been reset.")

@bot.tree.command(name="similarity", description="Changes the similarity threshold (Admin only)")
@app_commands.describe(threshold="New threshold value (0-100)")
async def similarity(interaction: discord.Interaction, threshold: int = None):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You need administrator permissions to use this command.", ephemeral=True)
        return
        
    global SIMILARITY_THRESHOLD
    if threshold is None:
        await interaction.response.send_message(f"Current similarity threshold is {SIMILARITY_THRESHOLD}.")
    else:
        if 0 <= threshold <= 100:
            SIMILARITY_THRESHOLD = threshold
            await interaction.response.send_message(f"Similarity threshold updated to {SIMILARITY_THRESHOLD}.")
        else:
            await interaction.response.send_message("Threshold must be between 0 and 100.")

@bot.tree.command(name="help", description="Shows all available commands and their descriptions")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="XNull Word Filtering Bot Commands",
        description="Here are all available commands:",
        color=discord.Color.blue()
    )
    
    # Add fields for each command
    embed.add_field(
        name="/filter [words]",
        value="Sets global filter words (Admin only)\nWords should be comma-separated",
        inline=False
    )
    
    embed.add_field(
        name="/ufilter [user] [words]",
        value="Sets filter words for a specific user (Admin only)\nWords should be comma-separated",
        inline=False
    )
    
    embed.add_field(
        name="/fwords",
        value="Displays the current global filter words",
        inline=False
    )
    
    embed.add_field(
        name="/uwords [user]",
        value="Displays filter words for all users or a specific user (Admin only)",
        inline=False
    )
    
    embed.add_field(
        name="/reset",
        value="Clears all global filter words (Admin only)",
        inline=False
    )
    
    embed.add_field(
        name="/ureset [users]",
        value="Clears filters for specific users or all users (Admin only)",
        inline=False
    )
    
    embed.add_field(
        name="/similarity [threshold]",
        value="Changes or displays the similarity threshold (Admin only)\nThreshold must be between 0-100",
        inline=False
    )
    
    embed.set_footer(text="XNull Word Filtering Bot | xnull.eu")
    
    await interaction.response.send_message(embed=embed)

bot_token = input("Please enter your bot token: ")
initial_filter_words = input("Please enter initial words to filter, separated by commas (or leave blank for none): ")

if initial_filter_words:
    filter_words = [word.strip() for word in initial_filter_words.split(',')]
    print(f"Initial filter words set to: {', '.join(filter_words)}")
else:
    print("No initial filter words set.")

bot.run(bot_token)
