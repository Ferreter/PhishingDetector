from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests


def check_url_threat(uri, api_key):
    # API url
    url = 'https://webrisk.googleapis.com/v1/uris:search'

    #All threat types in webrisk
    params = {
        'threatTypes': ['SOCIAL_ENGINEERING', 'MALWARE', 'UNWANTED_SOFTWARE', 'SOCIAL_ENGINEERING_EXTENDED_COVERAGE'],
        'uri': uri,
        'key': api_key
    }

    # Send the GET request
    response = requests.get(url, params=params)

    # Check the response status
    if response.status_code == 200:
        # Successful request
        data = response.json()
        
        # Check if the threat is present
        if 'threat' in data:
            threat_types = data['threat']['threatTypes']
            expire_time = data['threat']['expireTime']

            print(f"Threat Types: {threat_types}")
            print(f"Expire Time: {expire_time}")

            response_message = ""

            # Check for specific threat types
            if 'MALWARE' in threat_types:
                response_message += "Alert: The URL is identified as MALWARE. Malware can harm your device. Avoid clicking on the link to protect your data and device."
            elif 'SOCIAL_ENGINEERING' in threat_types:
                response_message += "Caution: The URL is identified as a SOCIAL ENGINEERING threat. Social engineering attempts to manipulate you. Do not proceed to the website and report the link."
            elif 'UNWANTED_SOFTWARE' in threat_types:
                response_message += "Warning: The URL is identified as UNWANTED SOFTWARE. Unwanted software can be harmful. Avoid interacting with the link to ensure your device's security."
            elif 'SOCIAL_ENGINEERING_EXTENDED_COVERAGE' in threat_types:
                response_message += "Attention: The URL is identified as a SOCIAL ENGINEERING (Extended Coverage) threat. Be cautious and avoid the website. Report the link to prevent potential harm."
            else:
                response_message += "The URL is safe from known threats."

            return response_message
        else:
            return "No threat information available. The URL is not on any threat lists.Proceed with caution\n\n\nRemember: New threats are created every day and even though Googles Webrisk list is regularly updated it is still possible to be threat"
    else:
        # Error handling
        return f"Error: {response.status_code}\n{response.text}"


#webrisk API
api_key = 'AIzaSyBsO6OGeF6ZXsqPFwEsSWIsOYPjHIKoGpQ'

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')
    
    
async def check_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Get the URL from the command parameters
    url_to_check = context.args[0] if context.args else None

    if url_to_check:
        response_message = check_url_threat(url_to_check, api_key)
        await update.message.reply_text(response_message)
    else:
        await update.message.reply_text('Please provide a URL to check. Use /check URL_GOES_HERE')


#telegram bot api key goes here 
app = ApplicationBuilder().token("6635501788:AAHEEP3hFf57zLZfH-XsqvcjNcRuzep0e_0").build()

app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("check", check_url))

app.run_polling()
