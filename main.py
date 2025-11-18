import requests
import datetime
import os
import sys
import random

# ==========================================
# ☁️ 配置区：读取 GitHub Secrets
# ==========================================
try:
    APP_ID = os.environ["APP_ID"]
    APP_SECRET = os.environ["APP_SECRET"]
    USER_ID = os.environ["USER_ID"]
    TEMPLATE_ID = os.environ["TEMPLATE_ID"]
    
    # 读取你刚才添加的 GPT_API_KEY
    GPT_API_KEY = os.environ.get("GPT_API_KEY") 
except KeyError:
    print("❌ 错误：Secrets 变量缺失！请检查 GitHub 设置")
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

# 🔥 核心升级：调用 GPT 生成情话
def get_gpt_message(weather, temp):
    if not GPT_API_KEY:
        return None 

    print("正在请求 GPT 生成文案...")
    
    # ✨ 这里设定 GPT 的人设 (你可以随意改)
    prompt = f"""
    你是一个温柔体贴的男朋友。你的女朋友叫“琪琪”。
    
    现在的天气情况是：
    - 城市：深圳
    - 天气：{weather}
    - 温度：{temp}
    
    请根据天气情况，写一段简短的早安问候语给琪琪。
    要求：
    1. 语气要超级宠溺、可爱，多用emoji表情。
    2. 如果天气不好（下雨、降温），一定要提醒她注意身体或带伞。
    3. 必须包含一句“早安”。
    4. 字数控制在 60 字以内。
    """

    headers = {
        "Authorization": f"Bearer {GPT_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-4o-mini", # 推荐用 4o-mini，便宜又聪明，如果没有权限则改回 gpt-3.5-turbo
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        url = "https://api.openai.com/v1/chat/completions"
        resp = requests.post(url, headers=headers, json=data, timeout=20)
        resp_json = resp.json()
        
        if "choices" in resp_json:
            content = resp_json["choices"][0]["message"]["content"]
            return content.strip()
        else:
            print(f"GPT API 返回异常: {resp_json}")
    except Exception as e:
        print(f"GPT 请求失败: {e}")
        
    return None

def get_love_words_fallback():
    """备用方案"""
    backups = [
        "琪琪早安！今天也是超级想你的一天鸭！❤️",
        "醒来觉得甚是爱你，要记得吃早饭哦！",
        "世界一般般，但你超甜。今天也要开心！",
    ]
    return random.choice(backups)

def send_message():
    token = get_access_token()
    if not token: return

    weather, temp = get_weather()
    
    # 优先尝试用 GPT 生成
    love_word = get_gpt_message(weather, temp)
    
    # 如果 GPT 失败了，就用备用情话
    if not love_word:
        print("⚠️ GPT 生成失败，使用备用情话")
        love_word = get_love_words_fallback()
    else:
        print(f"✅ GPT 生成成功: {love_word}")

    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    week_list = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    week_day = week_list[datetime.datetime.now().weekday()]

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
        print("✅ 推送成功！")
    else:
        print(f"❌ 推送失败: {resp}")

if __name__ == "__main__":
    send_message()
