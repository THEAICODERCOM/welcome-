# Discord Welcome Bot

A simple Discord bot that sends a customized welcome message when a new member joins the server.

## Features
- **Slash Command**: Use `/set_welcome_channel` to choose where welcome messages go.
- **Autocomplete**: The slash command provides a list of your server's text channels.
- **Dynamic Search**: Automatically finds and mentions your `#rules`, `#videos`, and `#general-chat` channels by searching for keywords.
- **Persistence**: Remembers your settings even after a restart.

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure the Bot**:
   - Open the `.env` file.
   - Replace the token with your actual Discord Bot Token.

3. **Discord Developer Portal Settings**:
   - Go to the [Discord Developer Portal](https://discord.com/developers/applications).
   - Select your application and go to the **Bot** tab.
   - **Crucial**: Enable **Server Members Intent** under the "Privileged Gateway Intents" section.
   - **Crucial**: Enable **Message Content Intent** if you want to use prefix commands (though slash commands are preferred).
   - Save Changes.

4. **Run the Bot**:
   ```bash
   python bot.py
   ```

## Usage
Once the bot is online, use the slash command in your server:
`/set_welcome_channel channel:#welcome-here`

The bot will then start sending the welcome message to that channel whenever someone joins!
