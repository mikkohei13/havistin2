import requests
import sys
from datetime import datetime, time

sys.path.append('../')
import app_secrets


def is_night_time():
   now = datetime.now().time()
   night_start = time(22, 0)
   night_end = time(7, 0)
   if night_start <= now <= night_end:
      return True
   return False

def send_text(bot_message, debug):

   period = ""

   if is_night_time():
      disable_notification_param = "&silent=true"
      period = " (night)" # debug
      print(period) # debug
   else:
      disable_notification_param = "&silent=false"
      period = " (night)" # debug
      print(period) # debug


   apiUrl = f"https://api.telegram.org/bot{ app_secrets.telegram_bot_token }/sendMessage?chat_id={ app_secrets.telegram_bot_chat_id }&parse_mode=Markdown{ disable_notification_param }&text={ bot_message }{ period }"

   # Are text and parse_mode deprecated? See https://core.telegram.org/method/messages.sendMessage

   if debug:
      print(bot_message)
   else:
      response = requests.get(apiUrl)
      return response.json()


#test = send_text("Sää on tavallinen: ", False) # debug
#print(test) # debug
