import requests
import datetime
import os
import sys
import random

# ==========================================
# ☁️ 配置区
# ==========================================
try:
    APP_ID = os.environ["APP_ID"]
    APP_SECRET = os.environ["APP_SECRET"]
    USER_ID = os.environ["USER_ID"]
    TEMPLATE_ID = os.environ["TEMPLATE_ID"]
    GPT_API_KEY = os.environ.get("GPT_API_KEY") 
except KeyError:
    print("❌ 错误：Secrets 变量缺失！")
    sys.exit(1)

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
            return today['weather'], f"{today['low']}℃ ~ {today['high']}℃"
    except:
        pass
    return "晴", "20℃ ~ 25℃"

def get_week_day_str():
    week_list = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return week_list[datetime.datetime.now().weekday()]

# 🔥 核心升级：更智能的 GPT 提示词
def get_gpt_message(weather, temp, week_day):
    if not GPT_API_KEY:
        return None 

    print("正在请求 GPT 生成更智能的文案...")
    
    # 👇 这里是“注入灵魂”的关键
    prompt = f"""
    你是一个超宠女朋友的男朋友，你的女朋友叫“琪琪”。
    
    【今日情报】
    - 城市：深圳
    - 天气：{weather}
    - 温度：{temp}
    - 今天是：{week_day}
    
    【任务要求】
    请给琪琪写一段早安微信，要求：
    1. 必须结合“天气”和“星期几”来发挥。
       - 比如周一要安慰她有“周一综合症”，周五要祝贺她马上解放。
       - 天气热要提醒防晒，下雨要提醒带伞，不要只报数据。
    2. 语气要自然、生活化，像是在被窝里发给她的。可以带点小幽默或撒娇。
    3. 结尾加一个温馨的建议（比如早餐吃什么，或者今天要喝奶茶）。
    4. 不要出现“亲爱的”这种老土的称呼，叫“宝”、“琪琪”或者“小猪”。
    5. 字数控制在 80 字以内，多用Emoji (✨💖☁️)。
    """

    headers = {
        "Authorization": f"Bearer {GPT_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-4o-mini", 
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8 # 调高一点，让它更活泼
    }

    try:
        url = "https://api.openai.com/v1/chat/completions"
        resp = requests.post(url, headers=headers, json=data, timeout=20)
        resp_json = resp.json()
        
        if "choices" in resp_json:
            return resp_json["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"GPT 请求失败: {e}")
        
    return None

def get_fallback_msg():
    return "琪琪早安！今天GitHub好像有点累，但我不累，依然超级爱你！记得吃早饭哦❤️"

def send_message():
    token = get_access_token()
    if not token: return

    weather, temp = get_weather()
    week_day = get_week_day_str()
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # 把星期几也传给 GPT，让它根据周几来写文案
    love_word = get_gpt_message(weather, temp, week_day)
    
    if not love_word:
        love_word = get_fallback_msg()

    url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={token}"
    
    data = {
        "touser": USER_ID,
        "template_id": TEMPLATE_ID,
        "data": {
            "date": {"value": f"{today_date} {week_day}", "color": "#FF69B4"},
            "city": {"value": CITY, "color": "#173177"},
            "weather": {"value": weather, "color": "#FFA500"},
            "temperature": {"value": temp, "color": "#00CC00"},
            "note": {"value": love_word, "color": "#FF1493"}
        }
    }
    
    resp = requests.post(url, json=data).json()
    if resp['errcode'] == 0:
        print(f"✅ 推送成功: {love_word}")
    else:
        print(f"❌ 推送失败: {resp}")

if __name__ == "__main__":
    send_message()
