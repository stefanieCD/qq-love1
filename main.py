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
# 👇 这里设置点击卡片后跳去哪里 (目前是深圳天气页，你可以换成任何网址)
CLICK_URL = "https://tianqi.qq.com/index.htm" 
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

# 🔥 核心升级：让 GPT 分两段输出
def get_gpt_message(weather, temp, week_day):
    if not GPT_API_KEY:
        return "今天也要开心呀！", "记得吃早饭哦！"

    print("正在请求 GPT 生成双段文案...")
    
    prompt = f"""
    你是一个超宠女朋友的男朋友，你的女朋友叫“琪琪”。
    今日情报：深圳，{weather}，{temp}，{week_day}。
    
    请生成两段话，中间用 "|||" 这个符号隔开：
    第一段（情话）：结合天气和星期几，写一段甜甜的问候，语气要软萌、宠溺，多用Emoji。
    第二段（建议）：给出一个具体的行动建议（如穿衣、带伞、喝奶茶、吃什么早餐）。
    
    例子格式：
    宝早安！今天周五啦，离见面又近了一步，深圳今天阳光很好，想和你一起晒太阳✨|||今天紫外线有点强，出门记得涂防晒，还要带上我送你的小水壶哦💧
    """

    headers = {
        "Authorization": f"Bearer {GPT_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-4o-mini", 
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8
    }

    try:
        url = "https://api.openai.com/v1/chat/completions"
        resp = requests.post(url, headers=headers, json=data, timeout=20)
        resp_json = resp.json()
        
        if "choices" in resp_json:
            content = resp_json["choices"][0]["message"]["content"].strip()
            # 尝试分割
            if "|||" in content:
                parts = content.split("|||")
                return parts[0].strip(), parts[1].strip()
            else:
                # 如果GPT没按套路出牌，就手动切一下或者当做一段
                return content, "今天要开开心心的！"
    except Exception as e:
        print(f"GPT 请求失败: {e}")
        
    return "琪琪早安！GitHub虽然累了，但我依然爱你❤️", "记得按时吃饭，照顾好自己！"

def send_message():
    token = get_access_token()
    if not token: return

    weather, temp = get_weather()
    week_day = get_week_day_str()
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # 获取两段文案
    msg_1, msg_2 = get_gpt_message(weather, temp, week_day)
    
    url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={token}"
    
    data = {
        "touser": USER_ID,
        "template_id": TEMPLATE_ID,
        "url": CLICK_URL, # 👈 这里添加了跳转链接，现在卡片可以点击了！
        "data": {
            "date": {"value": f"{today_date} {week_day}", "color": "#FF69B4"},
            "city": {"value": CITY, "color": "#173177"},
            "weather": {"value": weather, "color": "#FFA500"},
            "temperature": {"value": temp, "color": "#00CC00"},
            # 第一段：情话
            "love_msg": {"value": msg_1, "color": "#FF1493"},
            # 第二段：建议
            "suggestion": {"value": msg_2, "color": "#9370DB"}
        }
    }
    
    resp = requests.post(url, json=data).json()
    if resp['errcode'] == 0:
        print(f"✅ 推送成功")
    else:
        print(f"❌ 推送失败: {resp}")

if __name__ == "__main__":
    send_message()
