import discord
from discord.ext import commands
from fuzzywuzzy import fuzz
from discord.ext.commands import has_permissions, CheckFailure

# Bot configuration
PREFIX = '??'
SIMILARITY_THRESHOLD = 50  # Default value

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Remove the default help command
bot.remove_command('help')

# List of words to filter globally
filter_words = []
# Dictionary for user-specific filters
user_filters = {}

print(f"SIMILARITY_THRESHOLD is set to {SIMILARITY_THRESHOLD}. It is recommended to keep it at this value for optimal filtering.")

print("=== XNull Word Filtering Bot ===")
print("\nVisit https://www.xnull.eu for more projects and tools!")

# Before getting the bot token
print("\nTo get your bot token:")
print("1. Go to https://discord.com/developers/applications")
print("2. Click on your application (or create a new one)")
print("3. Go to the 'Bot' section")
print("4. Click 'Reset Token' or 'Copy' under the token section")
print("\nMake sure to keep your token secret and never share it with anyone!")
print("------------------------")

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
    activity = discord.Game(name="Type ??fwords to see filtered words") if filter_words else discord.Game(name="No filters set")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    
    print("\n=== Bot is ready! ===")
    print(f"\nInvite the bot to your server using this link:")
    print(f"\n{invite_link}\n")
    print("=" * 20)
    
    print(f'Logged in as {bot.user}')
    print("Initial global filter words:", ', '.join(filter_words) if filter_words else "None")

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
        for msg_word in message_words:
            if fuzz.ratio(msg_word, word_lower) >= SIMILARITY_THRESHOLD:
                await message.delete()
                return

    # Check user-specific filter words if they exist
    user_specific_words = user_filters.get(message.author.id, [])
    for word in user_specific_words:
        word_lower = word.lower()
        if word_lower in message_content_lower:
            await message.delete()
            break
        for msg_word in message_words:
            if fuzz.ratio(msg_word, word_lower) >= SIMILARITY_THRESHOLD:
                await message.delete()
                return

    await bot.process_commands(message)

@bot.command(name="filter", help="Sets global filter words. (Admin only) Usage: ??filter word1, word2")
@has_permissions(administrator=True)
async def change_filter_words(ctx, *, words):
    global filter_words
    filter_words = [word.strip() for word in words.split(',')]
    activity = discord.Game(name="Type ??fwords to see filtered words") if filter_words else discord.Game(name="No filters set")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    await ctx.send(f"Global filter words updated to: {', '.join(filter_words)}")

@bot.command(name="ufilter", help="Sets filter words for a specific user. (Admin only) Usage: ??ufilter @user word1, word2")
@has_permissions(administrator=True)
async def user_filter_words(ctx, user: discord.Member, *, words):
    user_filters[user.id] = [word.strip() for word in words.split(',')]
    await ctx.send(f"Custom filter words for {user.mention} updated to: {', '.join(user_filters[user.id])}")

@bot.command(name="fwords", help="Displays the global filter words. Usage: ??fwords")
async def show_global_filter_words(ctx):
    if filter_words:
        message = f"Global filter words: {', '.join(filter_words)}"
    else:
        message = "No global filter words set."
    await ctx.send(message)

@bot.command(name="uwords", help="Displays filter words for all users or a specific user. (Admin only) Usage: ??uwords or ??uwords @user")
@has_permissions(administrator=True)
async def show_user_filter_words(ctx, user: discord.Member = None):
    if user:
        # Display filter words for the specified user
        user_words = user_filters.get(user.id, [])
        if user_words:
            message = f"Filter words for {user.mention}: {', '.join(user_words)}"
        else:
            message = f"No filter words set for {user.mention}."
    else:
        # Display filter words for all users
        if user_filters:
            message = "User-specific filters:\n"
            user_filter_messages = [
                f"{await bot.fetch_user(user_id)}: {', '.join(words)}" if words else f"{await bot.fetch_user(user_id)}: No words set"
                for user_id, words in user_filters.items()
            ]
            message += "\n".join(user_filter_messages)
        else:
            message = "No user-specific filter words set."

    await ctx.send(message)

@bot.command(name="reset", help="Clears all global filter words. (Admin only) Usage: ??reset")
@has_permissions(administrator=True)
async def reset_global_filter(ctx):
    global filter_words
    filter_words.clear()
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="No filters set"))
    await ctx.send("Global filter words have been reset.")
    print("Global filter words reset.")

@bot.command(name="ureset", help="Clears all filters for specific users or all users. (Admin only) Usage: ??ureset @user1 @user2 or ??ureset")
@has_permissions(administrator=True)
async def reset_user_filters(ctx, *users: discord.Member):
    if users:
        for user in users:
            if user.id in user_filters:
                del user_filters[user.id]
        user_mentions = ', '.join(user.mention for user in users)
        await ctx.send(f"Filter words for the specified users ({user_mentions}) have been reset.")
        print(f"User-specific filters reset for: {user_mentions}")
    else:
        user_filters.clear()
        await ctx.send("All user-specific filter words have been reset.")
        print("All user-specific filters reset.")

@bot.command(name="similarity", help="Changes the similarity threshold. (Admin only) Usage: ??similarity <value>")
@has_permissions(administrator=True)
async def change_similarity_threshold(ctx, new_threshold: int = None):
    global SIMILARITY_THRESHOLD
    if new_threshold is None:
        await ctx.send(f"Current similarity threshold is {SIMILARITY_THRESHOLD}.")
    else:
        SIMILARITY_THRESHOLD = new_threshold
        await ctx.send(f"Similarity threshold updated to {SIMILARITY_THRESHOLD}.")
        print(f"Similarity threshold updated to {SIMILARITY_THRESHOLD}.")

@change_filter_words.error
@user_filter_words.error
@reset_global_filter.error
@reset_user_filters.error
@change_similarity_threshold.error
async def admin_command_error(ctx, error):
    if isinstance(error, CheckFailure):
        await ctx.send("You do not have permission to use this command. Only administrators can change filter settings.")

@bot.command(name='help', help="Displays all available commands. Usage: ??help")
async def help_command(ctx):
    embed = discord.Embed(title="Available Commands", color=discord.Color.blue())
    for command in bot.commands:
        if not command.hidden:
            embed.add_field(name=f"??{command.name}", value=command.help, inline=False)
    
    # Add footer text
    embed.set_footer(text="XNull Word Filtering Bot | xnull.eu")
    
    await ctx.send(embed=embed)

bot_token = input("Please enter your bot token: ")
initial_filter_words = input("Please enter initial words to filter, separated by commas (or leave blank for none): ")

if initial_filter_words:
    filter_words = [word.strip() for word in initial_filter_words.split(',')]
    print(f"Initial filter words set to: {', '.join(filter_words)}")
else:
    print("No initial filter words set.")

bot.run(bot_token)
