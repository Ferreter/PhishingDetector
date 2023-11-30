from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, Updater, CallbackContext, filters
import requests
import re

# Define language-specific message templates
EN_MESSAGES = {
    "greeting": "Hello {first_name}. Welcome to the Phishing Detector bot. You can use the following commands:\n"
                "/hello - Greet the bot\n"
                "/check URL - Check a URL for threats\n"
                "/language [en/fr/hi/zh] - Set the bot's language (default: en)",
    "provide_url": "Please provide a URL to check. Use **/check URL_GOES_HERE**",
    "malware_alert": "**Alert**: The URL is identified as **MALWARE**. Malware can harm your device. Avoid clicking on the link to protect your data and device.",
    "social_engineering_caution": "**Caution**: The URL is identified as a **SOCIAL ENGINEERING** threat. Social engineering attempts to manipulate you. Do not proceed to the website and report the link.",
    "unwanted_software_warning": "**Warning**: The URL is identified as **UNWANTED SOFTWARE**. Unwanted software can be harmful. Avoid interacting with the link to ensure your device's security.",
    "social_engineering_extended_caution": "**Attention**: The URL is identified as a **SOCIAL ENGINEERING (Extended Coverage)** threat. Be cautious and avoid the website. Report the link to prevent potential harm.",
    "no_threat_info": "No threat information available. The URL is not on any threat lists. Proceed with caution.\n\nRemember: New threats are created every day, and even though Google's Webrisk list is regularly updated, it is still possible to be a threat.",
    "uri_contains_numbers": "**Caution**: The URI contains numbers. When checking links, be mindful of unusual elements like numbers in the URL. Links with numbers might indicate suspicious activity. Exercise caution and consider verifying the source before clicking such links.",
    "uri_safe": "Tip: When checking links, pay attention to the structure of the URL. Unusual elements or unexpected characters may indicate potential risks. The current URI is free from numbers, but it's always good practice to stay vigilant when navigating the web."
}

FR_MESSAGES = {
    "greeting": "Bonjour {first_name}. Bienvenue sur le bot Phishing Detector. Vous pouvez utiliser les commandes suivantes :\n"
                "/hello - Saluer le bot\n"
                "/check URL - Vérifier une URL pour les menaces\n"
                "/language [en/fr/hi/zh] - Définir la langue du bot (par défaut : en)",
    "provide_url": "Veuillez fournir une URL à vérifier. Utilisez **/check URL_ICI**",
    "malware_alert": "**Alerte** : L'URL est identifiée comme **MALVEILLANTE**. Les logiciels malveillants peuvent endommager votre appareil. Évitez de cliquer sur le lien pour protéger vos données et votre appareil.",
    "social_engineering_caution": "**Mise en garde** : L'URL est identifiée comme une menace d'**INGÉNIERIE SOCIALE**. L'ingénierie sociale tente de vous manipuler. Ne continuez pas vers le site web et signalez le lien.",
    "unwanted_software_warning": "**Avertissement** : L'URL est identifiée comme **LOGICIEL NON SOUHAITÉ**. Les logiciels non souhaités peuvent être nuisibles. Évitez d'interagir avec le lien pour assurer la sécurité de votre appareil.",
    "social_engineering_extended_caution": "**Attention** : L'URL est identifiée comme une menace d'**INGÉNIERIE SOCIALE (couverture étendue)**. Soyez prudent et évitez le site web. Signalez le lien pour éviter tout dommage potentiel.",
    "no_threat_info": "Aucune information sur la menace n'est disponible. L'URL ne figure sur aucune liste de menaces. Procédez avec prudence.\n\nN'oubliez pas : de nouvelles menaces sont créées chaque jour, et même si la liste Webrisk de Google est régulièrement mise à jour, il est toujours possible qu'elle soit une menace.",
    "uri_contains_numbers": "**Mise en garde** : L'URI contient des chiffres. Lors de la vérification des liens, soyez attentif aux éléments inhabituels tels que les chiffres dans l'URL. Les liens contenant des chiffres peuvent indiquer une activité suspecte. Faites preuve de prudence et envisagez de vérifier la source avant de cliquer sur de tels liens.",
    "uri_safe": "Conseil : Lors de la vérification des liens, soyez attentif à la structure de l'URL. Des éléments inhabituels ou des caractères inattendus peuvent indiquer des risques potentiels. L'URI actuel ne contient pas de chiffres, mais il est toujours bon de rester vigilant lors de la navigation sur le Web."
}


HI_MESSAGES = {
    "greeting": "नमस्ते {first_name}. फिशिंग डिटेक्टर बॉट में आपका स्वागत है। आप निम्नलिखित कमांड्स का उपयोग कर सकते हैं:\n"
                "/hello - बॉट को नमस्कार कहें\n"
                "/check URL - URL की खतरों की जाँच करें\n"
                "/language [en/fr/hi/zh] - बॉट की भाषा सेट करें (डिफ़ॉल्ट: en)",
    "provide_url": "कृपया जांच करने के लिए एक URL प्रदान करें। **/check URL_GOES_HERE** का उपयोग करें",
    "malware_alert": "**चेतावनी:** URL को **MALWARE** के रूप में पहचाना गया है। मैलवेयर आपके डिवाइस को हानि पहुंचा सकता है। अपने डेटा और डिवाइस की सुरक्षा के लिए लिंक पर क्लिक करने से बचें।",
    "social_engineering_caution": "**सतर्कता:** URL को **सामाजिक इंजीनियरिंग** खतरा के रूप में पहचाना गया है। सामाजिक इंजीनियरिंग आपको मानव त्रुटि का उपयोग करके मनिपुरित करने का प्रयास करता है। वेबसाइट पर आगे न बढ़ें और लिंक की सूचना दें।",
    "unwanted_software_warning": "**चेतावनी:** URL को **अवांछित सॉफ़्टवेयर** के रूप में पहचाना गया है। अवांछित सॉफ़्टवेयर हानिकारक हो सकता है। अपने डिवाइस की सुरक्षा सुनिश्चित करने के लिए लिंक के साथ बातचीत न करें।",
    "social_engineering_extended_caution": "**ध्यान दें:** URL को **सामाजिक इंजीनियरिंग (विस्तारित कवरेज)** खतरा के रूप में पहचाना गया है। सतर्क रहें और वेबसाइट से बचें। पोटेंशियल हानि से बचाने के लिए लिंक की सूचना दें।",
    "no_threat_info": "कोई खतरा सूचना उपलब्ध नहीं है। URL को किसी भी खतरे की सूची पर नहीं रखा गया है। सतर्कता के साथ आगे बढ़ें।\n\nध्यान दें: नई खतरों को रोज़ बनाया जाता है, और यह भी सच है कि गूगल की वेबरिस्क सूची को नियमित रूप से अपडेट किया जाता है, फिर भी यह एक खतरा हो सकता है।",
    "uri_contains_numbers": "**सतर्कता:** URI में नंबर्स हैं। लिंक जाँचते समय URI में नंबर्स जैसे असामान्य तत्वों के प्रति सतर्क रहें। नंबर्स वाले लिंक संदेहपूर्ण गतिविधि की सूचना देने के रूप में हो सकते हैं। सतर्क रहें और इस तरह के लिंक पर क्लिक करने से पहले स्रोत की सत्यापन करने का विचार करें।",
    "uri_safe": "**सुझाव:** लिंक जाँचते समय URL की संरचना पर ध्यान दें। असामान्य तत्वों या अप्रत्याशित अक्षरों की ज्यादा वर्गीकरण संभावित खतरों की सूचना दे सकते हैं। मौजूदा URI में नंबर्स नहीं हैं, लेकिन वेब नेविगेशन करते समय सतर्क रहना हमेशा अच्छा अभ्यास है।",
}

ZH_MESSAGES = {
    "greeting": "你好 {first_name}。欢迎使用网络钓鱼检测器机器人。您可以使用以下命令：\n"
                "/hello - 与机器人打招呼\n"
                "/check URL - 检查URL是否存在威胁\n"
                "/language [en/fr/hi/zh] - 设置机器人的语言（默认：en）",
    "provide_url": "请提供要检查的URL。使用 /check URL_HERE",
    "malware_alert": "警告：URL被识别为MALWARE。恶意软件可能会损害您的设备。请避免单击链接以保护您的数据和设备。",
    "social_engineering_caution": "注意：URL被识别为社交工程威胁。社交工程试图操纵您。不要继续访问网站并报告链接。",
    "unwanted_software_warning": "警告：URL被识别为UNWANTED SOFTWARE。不受欢迎的软件可能会有害。避免与链接交互以确保设备的安全。",
    "social_engineering_extended_caution": "注意：URL被识别为社交工程（扩展覆盖）威胁。请小心并避免访问网站。报告链接以防止潜在危害。",
    "no_threat_info": "没有威胁信息可用。该URL不在任何威胁列表中。请谨慎行事。\n\n请记住：每天都会出现新的威胁，尽管Google的Webrisk列表定期更新，但仍有可能存在威胁。",
    "uri_contains_numbers": "警告：URI中包含数字。在检查链接时，请注意URL中的数字等异常元素。带有数字的链接可能表示可疑活动。在单击此类链接之前要谨慎，考虑验证来源。",
    "uri_safe": "提示：在检查链接时，请注意URL的结构。异常元素或意外字符可能表示潜在风险。当前的URI不包含数字，但在浏览网络时保持警惕始终是一个好习惯。",
    
}

current_language = "en"  # Default to English

def check_numbers_in_uri(uri):
    digit_pattern = re.compile(r'\d')

    if digit_pattern.search(uri):
        return (
            EN_MESSAGES["uri_contains_numbers"]
            if current_language == "en"
            else FR_MESSAGES["uri_contains_numbers"]
            if current_language == "fr"
            else HI_MESSAGES["uri_contains_numbers"]
            if current_language == "hi"
            else ZH_MESSAGES["uri_contains_numbers"]
        )
    else:
        return (
            EN_MESSAGES["uri_safe"]
            if current_language == "en"
            else FR_MESSAGES["uri_safe"]
            if current_language == "fr"
            else HI_MESSAGES["uri_safe"]
            if current_language == "hi"
            else ZH_MESSAGES["uri_safe"]
        )

def check_url_threat(uri, api_key):
    url = 'https://webrisk.googleapis.com/v1/uris:search'

    params = {
        'threatTypes': ['SOCIAL_ENGINEERING', 'MALWARE', 'UNWANTED_SOFTWARE', 'SOCIAL_ENGINEERING_EXTENDED_COVERAGE'],
        'uri': uri,
        'key': api_key
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        
        if 'threat' in data:
            threat_types = data['threat']['threatTypes']
            expire_time = data['threat']['expireTime']

            response_message = ""

            if 'MALWARE' in threat_types:
                response_message += (
                    EN_MESSAGES["malware_alert"]
                    if current_language == "en"
                    else FR_MESSAGES["malware_alert"]
                    if current_language == "fr"
                    else HI_MESSAGES["malware_alert"]
                    if current_language == "hi"
                    else ZH_MESSAGES["malware_alert"]
                )
                response_message += "\n\n"+check_numbers_in_uri(uri)
            elif 'SOCIAL_ENGINEERING' in threat_types:
                response_message += (
                    EN_MESSAGES["social_engineering_caution"]
                    if current_language == "en"
                    else FR_MESSAGES["social_engineering_caution"]
                    if current_language == "fr"
                    else HI_MESSAGES["social_engineering_caution"]
                    if current_language == "hi"
                    else ZH_MESSAGES["social_engineering_caution"]
                )
                response_message += "\n\n"+check_numbers_in_uri(uri)
            elif 'UNWANTED_SOFTWARE' in threat_types:
                response_message += (
                    EN_MESSAGES["unwanted_software_warning"]
                    if current_language == "en"
                    else FR_MESSAGES["unwanted_software_warning"]
                    if current_language == "fr"
                    else HI_MESSAGES["unwanted_software_warning"]
                    if current_language == "hi"
                    else ZH_MESSAGES["unwanted_software_warning"]
                )
                response_message += "\n\n"+check_numbers_in_uri(uri)
            elif 'SOCIAL_ENGINEERING_EXTENDED_COVERAGE' in threat_types:
                response_message += (
                    EN_MESSAGES["social_engineering_extended_caution"]
                    if current_language == "en"
                    else FR_MESSAGES["social_engineering_extended_caution"]
                    if current_language == "fr"
                    else HI_MESSAGES["social_engineering_extended_caution"]
                    if current_language == "hi"
                    else ZH_MESSAGES["social_engineering_extended_caution"]
                )
                response_message += "\n\n"+check_numbers_in_uri(uri)
            else:
                response_message += (
                    EN_MESSAGES["no_threat_info"]
                    if current_language == "en"
                    else FR_MESSAGES["no_threat_info"]
                    if current_language == "fr"
                    else HI_MESSAGES["no_threat_info"]
                    if current_language == "hi"
                    else ZH_MESSAGES["no_threat_info"]
                )

            return response_message
        else:
            return (
                EN_MESSAGES["no_threat_info"]
                if current_language == "en"
                else FR_MESSAGES["no_threat_info"]
                if current_language == "fr"
                else HI_MESSAGES["no_threat_info"]
                if current_language == "hi"
                else ZH_MESSAGES["no_threat_info"]
            )
    else:
        return f"Error: {response.status_code}\n{response.text}"
 

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global current_language
    text = context.args[0].lower() if context.args else ""
    
    if text == "fr":
        current_language = "fr"
    elif text == "hi":
        current_language = "hi"
    elif text == "zh":
        current_language = "zh"
    else:
        current_language = "en"
    
    await update.message.reply_text("Language set to " + current_language.upper())

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    greeting_message = (
        EN_MESSAGES["greeting"]
        if current_language == "en"
        else FR_MESSAGES["greeting"]
        if current_language == "fr"
        else HI_MESSAGES["greeting"]
        if current_language == "hi"
        else ZH_MESSAGES["greeting"]
    )
    await update.message.reply_text(greeting_message.format(first_name=user.first_name))


async def check_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    url_to_check = context.args[0] if context.args else None

    if url_to_check:
        response_message = check_url_threat(url_to_check, api_key)
        if("कोई खतरा सूचना उपलब्ध नहीं" in response_message) or ("没有威胁信息可用。该URL不在任何威胁列表中" in response_message) or ("Aucune information sur la menace" in response_message) or ("No threat information available" in response_message):
            # Replace 'path_to_image' with the actual path to the image file you want to send
            path_to_image = 'media/images/authentic.png'

            # Send the image as a reply to the user's message
            with open(path_to_image, 'rb') as image_file:
                await update.message.reply_photo(photo=InputFile(image_file))
        else:
            # Replace 'path_to_image' with the actual path to the image file you want to send
            path_to_image = 'media/images/scam.png'

            # Send the image as a reply to the user's message
            with open(path_to_image, 'rb') as image_file:
                await update.message.reply_photo(photo=InputFile(image_file))
    else:
        response_message = (
            EN_MESSAGES["provide_url"]
            if current_language == "en"
            else FR_MESSAGES["provide_url"]
            if current_language == "fr"
            else HI_MESSAGES["provide_url"]
            if current_language == "hi"
            else ZH_MESSAGES["provide_url"]
        )

    await update.message.reply_text(response_message)


   
async def handle_text(update, context):


   
    # Respond with a default message
    await update.message.reply_text("I received your message, but I'm not sure how to respond. \n\n You can use the following commands:\n"
            "/hello - Greet the bot\n"
            "/check URL - Check a URL for threats\n"
            "/language [en/fr/hi/zh] - Set the bot's language (default: en)")

# Define your Webrisk API key
api_key = 'YOUR_GOOGLE_API_KEY'

app = ApplicationBuilder().token("YOUR_TELEGRAM_BOT_TOKEN").build()

app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("check", check_url))
app.add_handler(CommandHandler("language", set_language))
app.add_handler(MessageHandler(filters.TEXT, handle_text))

app.run_polling()

