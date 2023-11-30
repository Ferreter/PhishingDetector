# Phishing Detector Bot

The Phishing Detector Bot is a Telegram bot designed to help users identify potentially harmful URLs. It utilizes the Google Webrisk API to check URLs for various threat types, including malware, social engineering, and unwanted software. The bot can communicate with users in multiple languages and provides real-time threat assessments for URLs.

## Features

- **URL Threat Checking**: Users can send URLs to the bot, and it will check them for threats using the Google Webrisk API.

- **Multi-Language Support**: The bot supports multiple languages, including English, French, Hindi, and Chinese. Users can set their preferred language using the `/language` command.

- **Threat Notifications**: The bot provides threat notifications for URLs that are identified as malware, social engineering, or unwanted software. It also offers additional cautionary messages for certain cases.

- **Image Responses**: When a URL is checked, the bot responds with appropriate images to indicate whether the URL is safe or potentially harmful.

## Commands

- `/hello`: Greet the bot and receive a welcome message in the selected language.

- `/check URL`: Check a URL for potential threats. Replace `URL` with the actual URL you want to check.

- `/language [en/fr/hi/zh]`: Set the bot's language preference. You can choose from English (en), French (fr), Hindi (hi), or Chinese (zh). The default language is English.

## Usage

1. Start a conversation with the bot on Telegram.

2. Use the `/hello` command to greet the bot and receive a welcome message in your preferred language.

3. Use the `/language` command to set your preferred language if needed.

4. To check a URL for threats, use the `/check` command followed by the URL you want to check. For example, `/check https://example.com`.

5. The bot will respond with threat information and an image indicating the status of the URL (safe or potentially harmful).

## Configuration

To run the bot, you need to configure the following:

- **Google Webrisk API Key**: Replace the placeholder `YOUR_GOOGLE_API_KEY` with your actual API key obtained from Google Webrisk. You can get the API key by signing up for the Google Webrisk service.

- **Telegram Bot Token**: Replace the placeholder `YOUR_TELEGRAM_BOT_TOKEN` with your Telegram bot token. You can create a bot and obtain the token by following the instructions on the [Telegram BotFather](https://core.telegram.org/bots#botfather) page.

## Running the Bot

You can run the bot by executing the script. Ensure that you have installed the required dependencies.

```bash
python your_bot_script.py
```
## Disclaimer
The Phishing Detector Bot is designed for informational purposes and does not guarantee the complete security of URLs. Users should exercise caution when interacting with URLs and avoid clicking on suspicious links.
