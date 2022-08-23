from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random
from zhdate import ZhDate as lunar_date
from datetime import datetime

today = datetime.now()
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_ids = os.environ["USER_ID"].split("\n")
template_id = os.environ["TEMPLATE_ID"]
last_back=os.environ["LAST_BACK"]

def get_weather():
  url = "http://t.weather.sojson.com/api/weather/city/" + city
  res = requests.get(url).json()
  weather = res['data']['forecast'][0]
  return weather['type'], res['data']['wendu'],weather['high'], weather['low'], weather['notice']

def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

def get_back():
  next = datetime.strptime(str(date.today().year) + "-" + last_back +' 23:59:59', "%Y-%m-%d %H:%M:%S")
  if (next-today).days>=0:
    return "距离下次回来还有%d天" % (next-today).days
  else :
    return "距离上次回来已经过去%d天" % (today-next).days
  
def get_birthday():
  next = datetime.strptime(str(date.today().year).replace(year=next.year - 1) + "-" + birthday +' 23:59:59', "%Y-%m-%d %H:%M:%S")
  next = next.to_datetime()
  if next <= datetime.now():
    next = datetime.strptime(str(date.today().year) + "-" + birthday +' 23:59:59', "%Y-%m-%d %H:%M:%S")
    next = next.to_datetime()
  elif next.replace(year=next.year + 1).to_datetime()<datetime.now():
    next = next.replace(year=next.year + 2)
    next = next.to_datetime()
  return (next - today).days

def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  return words.json()['data']['text']

def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient(app_id, app_secret)

wm = WeChatMessage(client)
wea, temperature, highest, lowest,notice = get_weather()
data = {"weather":{"value":wea,"color":get_random_color()},"notice":{"value":notice,"color":get_random_color()},"date":{"value":today.strftime("%m-%d"),"color":get_random_color()},"temperature":{"value":temperature,"color":get_random_color()},"love_days":{"value":get_count(),"color":get_random_color()},"birthday_left":{"value":get_birthday(),"color":get_random_color()},"words":{"value":get_words(),"color":get_random_color()},"highest": {"value":highest,"color":get_random_color()},"lowest":{"value":lowest, "color":get_random_color()},"last_back":{"value":get_back(), "color":get_random_color()}}
count = 0
for user_id in user_ids:
  res = wm.send_template(user_id, template_id, data)
  count+=1

print("发送了" + str(count) + "条消息")
