import requests
import datetime
import os
import sys

# ==========================================
# ☁️ 配置区
# ==========================================
try:
    APP_ID = os.environ["APP_ID"]
    APP_SECRET = os.environ["APP_SECRET"]
    TEMPLATE_ID = os.environ["TEMPLATE_ID"]
    GPT_API_KEY = os.environ.get("GPT_API_KEY") 
except KeyError:
    print("❌ 错误：Secrets 变量缺失！")
    sys.exit(1)

USERS = [
    "o13257d7f-0B3aLMx8UGIAaGZkUY", 
    "o13257XIz2XpWkacUw08fny0mNyE"
]

CITY = "深圳"
CLICK_URL = "https://tianqi.qq.com/index.htm"
# ==========================================

def get_access_token():
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APP_ID}&secret={APP_SECRET}"
    try:
        resp = requests.get(url).json()
        return resp.get('access_token')
    except:
        return None

def get_weather():
    try:
        url = f"http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city={CITY}"
        res = requests.get(url).json()
        if res and res['data'] and res['data']['list']:
            today = res['data']['list'][0]
            return f"{CITY} | {today['weather']} | {today['low']}~{today['high']}℃"
    except:
        pass
    return f"{CITY} | 晴 | 25℃"

def get_gpt_message():
    if not GPT_API_KEY:
        return "没有GPT Key，但我依然爱你！", "记得喝水"
    
    # 简单粗暴的 Prompt
    prompt = "请生成两句话，用|||隔开。第一句是给女朋友琪琪的超甜早安情话（20字内），第二句是温馨提醒（10字内）。"
    
    headers = {"Authorization": f"Bearer {GPT_API_KEY}"}
    data = {
        "model": "gpt-4o-mini", 
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        url = "https://api.openai-proxy.com/v1/chat/completions"
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        content = resp.json()["choices"][0]["message"]["content"].strip()
        if "|||" in content:
            parts = content.split("|||")
            return parts[0].strip(), parts[1].strip()
        return content[:20], "今天要开心"
    except Exception as e:
        print(f"GPT Error: {e}")
        return "李杨最爱琪琪！(GPT卡了)", "记得按时吃饭"

def send_message():
    token = get_access_token()
    if not token: return

    weather_info = get_weather()
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    msg_1, msg_2 = get_gpt_message()
    
    print(f"准备发送内容: info={msg_1}, tips={msg_2}") # 打印出来看看

    for user_id in USERS:
        url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={token}"
        data = {
            "touser": user_id,
            "template_id": TEMPLATE_ID,
            "url": CLICK_URL,
            "data": {
                # 对应网页上的 {{date.DATA}}
                "date": {"value": today_date, "color": "#FF69B4"},
                # 对应网页上的 {{weather.DATA}}
                "weather": {"value": weather_info, "color": "#173177"},
                # 对应网页上的 {{info.DATA}}  <-- 重点是这个
                "info": {"value": msg_1, "color": "#FF1493"},
                # 对应网页上的 {{tips.DATA}}  <-- 和这个
                "tips": {"value": msg_2, "color": "#9370DB"}
            }
        }
        resp = requests.post(url, json=data).json()
        print(f"发送给 {user_id}: {resp}")

if __name__ == "__main__":
    send_message()
