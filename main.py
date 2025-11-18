import requests
import datetime
import os
import sys
import random

# ==========================================
# ☁️ 云端版：自动读取你填在 Secrets 里的密码
# ==========================================
try:
    APP_ID = os.environ["APP_ID"]
    APP_SECRET = os.environ["APP_SECRET"]
    USER_ID = os.environ["USER_ID"]
    TEMPLATE_ID = os.environ["TEMPLATE_ID"]
except KeyError:
    print("❌ 错误：Secrets 没填对！请检查 GitHub Settings")
    sys.exit(1)

# 💖 城市：深圳
CITY = "深圳"
# ==========================================

def get_access_token():
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APP_ID}&secret={APP_SECRET}"
    try:
        resp = requests.get(url).json()
        if 'access_token' in resp:
            return resp['access_token']
    except Exception as e:
        print(f"Token获取失败: {e}")
    return None

def get_weather():
    try:
        url = f"http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city={CITY}"
        res = requests.get(url).json()
        if res and res['data'] and res['data']['list']:
            today = res['data']['list'][0]
            weather = today['weather']
            low = int(today['low'])
            high = int(today['high'])
            
            # 💖 专属暖心提示
            tips = ""
            if low < 15:
                tips = " (宝，天冷记得穿厚点🧣)"
            elif high > 29:
                tips = " (太热啦，注意防晒鸭☂️)"
            elif "雨" in weather:
                tips = " (带伞带伞！别淋湿了☔)"
                
            return weather, f"{low}℃ ~ {high}℃{tips}"
    except:
        pass
    return "晴", "20℃ ~ 25℃"

def get_love_words():
    # 备用甜言蜜语库
    words = [
        "醒来觉得甚是爱你。",
        "今天也是超级想见琪琪的一天！",
        "要在天亮前变成小星星，去偷亲你的眼睛。",
        "你就是我最甜的糖果。",
        "琪琪早安，今天要开心哦！",
        "世界一般般，但你超甜。"
    ]
    try:
        # 尝试抓取在线情话
        url = "https://api.uomg.com/api/rand.qinghua?format=json"
        res = requests.get(url).json()
        if res and 'content' in res:
            return res['content']
    except:
        pass
    return random.choice(words)

def get_week_day():
    week_list = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    return week_list[datetime.datetime.now().weekday()]

def send_message():
    token = get_access_token()
    if not token: return

    weather, temp = get_weather()
    love_word = get_love_words()
    today_date = datetime.datetime.now().strftime("%Y-%m-%d") + " " + get_week_day()

    url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={token}"
    
    data = {
        "touser": USER_ID,
        "template_id": TEMPLATE_ID,
        "data": {
            "date": {"value": today_date, "color": "#FF69B4"}, 
            "city": {"value": CITY, "color": "#173177"},
            "weather": {"value": weather, "color": "#FFA500"},
            "temperature": {"value": temp, "color": "#00CC00"},
            "note": {"value": love_word, "color": "#FF1493"} 
        }
    }
    
    resp = requests.post(url, json=data).json()
    if resp['errcode'] == 0:
        print("✅ 推送成功！")
    else:
        print(f"❌ 推送失败: {resp}")

if __name__ == "__main__":
    send_message()
