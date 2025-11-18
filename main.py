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
    TEMPLATE_ID = os.environ["TEMPLATE_ID"]
    GPT_API_KEY = os.environ.get("GPT_API_KEY") 
except KeyError:
    print("❌ 错误：Secrets 变量缺失！")
    sys.exit(1)

# 👥 接收人列表
USERS = [
    "o13257d7f-0B3aLMx8UGIAaGZkUY",  # 琪琪 (煤气)
    "o13257XIz2XpWkacUw08fny0mNyE"   # 李杨 (煤气罐)
]

CITY = "深圳"
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
            # 简化天气显示，省空间
            return today['weather'], f"{today['low']}~{today['high']}℃"
    except:
        pass
    return "晴", "25℃"

def get_week_day_str():
    week_list = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return week_list[datetime.datetime.now().weekday()]

def get_gpt_message(weather, temp, week_day):
    if not GPT_API_KEY:
        return "煤气早安！爱你❤️", "记得吃早饭！"

    print("正在请求 GPT 生成精简文案...")
    
    # 🔥 核心修改：极简模式 Prompt
    prompt = f"""
    【角色】李杨（北邮研究生，煤气罐） x 江琪（中大本科生，煤气）。
    【情报】深圳 {weather} {temp} {week_day}。
    
    【任务】
    生成两句极短的话，用 "|||" 隔开：
    1. 第一句(love_msg)：一句话情书。必须**超级简短**（20字以内），甜度爆表，一眼心动。
    2. 第二句(suggestion)：最核心的叮嘱（10字以内）。
    
    【反例(太长不要)】：
    今天天气变冷了，你要记得多穿衣服，不要着凉了... (❌ 这种会被微信折叠)
    
    【正例(要这种)】：
    降温了，想把你揣进我的口袋里取暖✨|||乖乖穿厚外套🧣
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
        url = "https://api.openai-proxy.com/v1/chat/completions"
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        resp_json = resp.json()
        
        if "choices" in resp_json:
            content = resp_json["choices"][0]["message"]["content"].strip()
            if "|||" in content:
                parts = content.split("|||")
                return parts[0].strip(), parts[1].strip()
            else:
                return content[:20], "今天要开心！"
    except Exception as e:
        print(f"GPT 请求失败: {e}")
        
    return "GitHub卡了，但我依然爱你❤️", "照顾好自己"

def send_message():
    token = get_access_token()
    if not token: return

    weather, temp = get_weather()
    week_day = get_week_day_str()
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # 获取精简文案
    msg_1, msg_2 = get_gpt_message(weather, temp, week_day)
    
    for user_id in USERS:
        print(f"☁️ 正在发送给: {user_id}")
        url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={token}"
        
        data = {
            "touser": user_id,
            "template_id": TEMPLATE_ID,
            "url": CLICK_URL, 
            "data": {
                "date": {"value": f"{today_date} {week_day}", "color": "#FF69B4"},
                "city": {"value": CITY, "color": "#173177"},
                "weather": {"value": weather, "color": "#FFA500"},
                "temperature": {"value": temp, "color": "#00CC00"},
                # 这里的颜色我调成了更醒目的深粉色
                "love_msg": {"value": msg_1, "color": "#FF1493"},   
                "suggestion": {"value": msg_2, "color": "#9370DB"}  
            }
        }
        
        resp = requests.post(url, json=data).json()
        if resp['errcode'] == 0:
            print(f"✅ 发送成功！")
        else:
            print(f"❌ 发送失败: {resp}")

if __name__ == "__main__":
    send_message()
