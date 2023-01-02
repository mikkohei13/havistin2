import requests
import sys

sys.path.append('../')
import app_secrets

def send_text(bot_message, debug):
   apiUrl = "https://api.telegram.org/bot" + app_secrets.telegram_bot_token + "/sendMessage?chat_id=" + app_secrets.telegram_bot_chat_id + "&parse_mode=Markdown&text=" + bot_message

   if debug:
      print(bot_message)
   else:
      response = requests.get(apiUrl)
      return response.json()


#test = send_text("Sää on talvinen.", False)
#print(test)

