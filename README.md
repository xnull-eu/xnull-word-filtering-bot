# XNull Word Filtering Bot

A powerful Discord word filtering bot with fuzzy matching capabilities to catch attempted filter bypasses and user-specific filtering.

Visit [xnull.eu](https://www.xnull.eu) for more projects and tools!

## Features

- Word and sentence filtering with fuzzy matching
- Global and user-specific filters
- Similarity threshold control
- Multiple word filtering
- Bypass protection
- Administrator controls
- Simple and intuitive commands
- Dynamic status display showing filtered words

## Commands

- `/help` - Shows all available commands
- `/filter [words]` - Set global filter words (Admin only)
- `/fwords` - Display currently filtered words
- `/similarity [value]` - Show or change similarity threshold (Admin only)
- `/ufilter @user [words]` - Set filters for specific users (Admin only)
- `/uwords [@user]` - Show filters for all users or specific user (Admin only)
- `/reset` - Clear all global filter words (Admin only)
- `/ureset [@users]` - Clear filters for specific or all users (Admin only)

## How It Works

### Word Filtering
- Filters individual words and sentences
- Supports multiple words (separated by commas)
- Example: `??filter water, bad, test`
- Detects filtered words within sentences (e.g., "I drink water" gets deleted if "water" is filtered)

### User-Specific Filtering
- Set filters for individual users
- Manage filters separately from global filters
- Example: `??ufilter @user water, bad`
- Reset filters for specific users or all users

### Similarity Detection
- Default similarity threshold: 50
- Higher threshold (e.g., 80) = Stricter matching (only catches close matches like "wat3r")
- Lower threshold (e.g., 30) = Looser matching (catches more variations like "w@73r")
- Adjust with `??similarity [value]` command

### Examples
- Filtering "water":
  - Will catch: "water", "wat3r", "w@ter", "I drink water", "I drink w@t3r"
  - Won't catch: "waterfall", "underwater"
- Filtering exact phrases:
  - Use: `??filter this is a sentence`
  - Will catch the exact phrase and similar variations

## Requirements

- Python 3.8 or higher
- discord.py
- fuzzywuzzy
- python-Levenshtein (for better fuzzy matching performance)

## Setup

1. Create a Discord Bot:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Go to the Bot section
   - Create a bot and copy the token

2. Clone the repository:
    ```
    git clone https://github.com/xnull-eu/xnull-word-filtering-bot.git
    cd xnull-word-filtering-bot
    ```

3. Install requirements:
    ```
    pip install -r requirements.txt
    ```

4. Run the bot:
    ```
    python "main.py"
    ```
    
5. Enter your bot token when prompted
6. Enter any initial filter words (optional)
7. Use the bot's invite link to add it to your server

## Building Executable

To create a standalone executable:

1. Install requirements
2. Run the build script:
    ```
    python build.py
    ```

3. Find the executable in the `dist` folder

## Features in Detail

### Fuzzy Matching
- Uses fuzzy string matching to detect similar words
- Helps prevent filter bypassing attempts
- Configurable similarity threshold
- Real-time message scanning

### Administrator Controls
- Only administrators can modify filters
- Only administrators can change similarity threshold
- All users can view current filtered words
- Secure permission checking

### Dynamic Status
- Bot status shows current filtered words
- Updates automatically when filters change
- Shows "No filters set" when empty

## Support

For issues, suggestions, or contributions, please visit [xnull.eu](https://www.xnull.eu)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper
- [fuzzywuzzy](https://github.com/seatgeek/fuzzywuzzy) - Fuzzy string matching
- [python-Levenshtein](https://github.com/ztane/python-Levenshtein/) - Fast string matching computations
