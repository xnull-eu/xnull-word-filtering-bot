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

# List of words to filter, initially empty
filter_words = []

# Message to display in the command prompt
print(f"SIMILARITY_THRESHOLD is set to {SIMILARITY_THRESHOLD}. It is recommended to keep it at this value for optimal filtering.")

# At the start of the script, before getting the bot token
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
    # Check if the message is from a bot
    if message.author.bot:
        return

    # Filter messages based on current patterns
    for pattern in filter_words:
        if fuzz.ratio(message.content.lower(), pattern.strip().lower()) >= SIMILARITY_THRESHOLD:
            await message.delete()
            break  # Exit the loop once a match is found

    # Process other commands
    await bot.process_commands(message)

@bot.command(name="filter", help="Changes the words being filtered. (Admin only) Usage: ??filter word1, word2, word3")
@has_permissions(administrator=True)
async def change_filter_words(ctx, *, words):
    """
    This command updates the filtered words and the bot's activity dynamically.
    Only users with the Administrator permission can use this command.
    Usage: ??filter example1, example2, example3
    """
    global filter_words

    # Split the words by commas and update the filter list
    filter_words = [word.strip() for word in words.split(',')]

    # Update bot's activity to reflect the new filter words
    filtered_words_display = ', '.join(filter_words)
    activity = discord.Game(name=f"Filtering: {filtered_words_display}")
    await bot.change_presence(status=discord.Status.online, activity=activity)

    # Let the user know the filter words were updated
    await ctx.send(f"Filter words updated to: {filtered_words_display}")
    print(f"Filter words updated to: {filtered_words_display}")

@change_filter_words.error
async def change_filter_words_error(ctx, error):
    """
    Error handling for the ??filter command.
    If a user without Administrator permission tries to use the command, this will notify them.
    """
    if isinstance(error, CheckFailure):
        await ctx.send("You do not have permission to use this command. Only administrators can change the filter words.")

@bot.command(name="fwords", help="Displays the currently filtered words. Usage: ??fwords")
async def show_filter_words(ctx):
    """
    This command shows the currently set filter words.
    Usage: ??fwords
    """
    if filter_words:
        filtered_words_display = ', '.join(filter_words)
        await ctx.send(f"Currently filtered words: {filtered_words_display}")
    else:
        await ctx.send("No words are currently being filtered.")

@bot.command(name="similarity", help="Changes the similarity threshold. (Admin only) Usage: ??similarity <value>")
@has_permissions(administrator=True)
async def change_similarity_threshold(ctx, new_threshold: int = None):
    """
    This command changes or shows the current similarity threshold.
    Only administrators can change the threshold.
    Usage: ??similarity <value>
    """
    global SIMILARITY_THRESHOLD

    if new_threshold is None:
        # If no new value is provided, show the current threshold
        await ctx.send(f"Current similarity threshold is {SIMILARITY_THRESHOLD}.")
    else:
        # Update the similarity threshold
        SIMILARITY_THRESHOLD = new_threshold
        await ctx.send(f"Similarity threshold updated to {SIMILARITY_THRESHOLD}.")
        print(f"Similarity threshold updated to {SIMILARITY_THRESHOLD}.")

@change_similarity_threshold.error
async def change_similarity_threshold_error(ctx, error):
    """
    Error handling for the ??similarity command.
    If a user without Administrator permission tries to use the command, this will notify them.
    """
    if isinstance(error, CheckFailure):
        await ctx.send("You do not have permission to use this command. Only administrators can change the similarity threshold.")

# Custom help command
@bot.command(name='help', help="Displays all available commands. Usage: ??help")
async def help_command(ctx):
    """
    Custom help command that displays all available commands.
    """
    embed = discord.Embed(title="Available Commands", color=discord.Color.blue())
    
    for command in bot.commands:
        if not command.hidden:  # Avoid showing hidden commands
            embed.add_field(name=f"??{command.name}", value=command.help, inline=False)
    
    # Add footer text
    embed.set_footer(text="XNull Word Filtering Bot | xnull.eu")
    
    await ctx.send(embed=embed)

# Ask the user for the bot token and initial filter words at runtime
bot_token = input("Please enter your bot token: ")
initial_filter_words = input("Please enter initial words to filter, separated by commas (or leave blank for none): ")

# If the user provides initial words, populate the filter_words list
if initial_filter_words:
    filter_words = [word.strip() for word in initial_filter_words.split(',')]
    print(f"Initial filter words set to: {', '.join(filter_words)}")
else:
    print("No initial filter words set.")

# Run the bot
bot.run(bot_token)
