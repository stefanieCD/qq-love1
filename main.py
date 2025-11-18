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

# 👥 接收人列表 (把所有人的ID都放在这里)
USERS = [
    "o13257d7f-0B3aLMx8UGIAaGZkUY",  # 琪琪 (煤气)
    "o13257XIz2XpWkacUw08fny0mNyE"   # 新增的用户
]

CITY = "深圳"
# 点击卡片跳转的地址 (比如深圳天气页)
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

def get_gpt_message(weather, temp, week_day):
    """生成李杨给琪琪的早安"""
    if not GPT_API_KEY:
        return "煤气早安！今天也是爱你的一天❤️", "记得吃早饭，照顾好自己！"

    print("正在请求 GPT 生成文案...")
    
    prompt = f"""
    【角色设定】
    你叫“李杨”（昵称：杨杨、煤气罐），北邮研究生。
    女朋友叫“江琪”（昵称：琪琪、煤气），中大商学院本科生。
    
    【今日情报】
    深圳，{weather}，{temp}，{week_day}。
    
    【任务】
    生成两段话，用 "|||" 隔开：
    第一段（情话）：语气宠溺、稳重但深情。结合天气/周几/异地恋/学校生活写。
    第二段（建议）：温馨的日常嘱咐（防晒/带伞/喝水/心情）。
    
    例子：
    煤气早安！今天周五啦，刚才在实验室就在想你，深圳降温了，要乖乖穿外套哦✨|||今天风大，出门记得戴好我送你的围巾，不许只要风度不要温度🧣
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
        # 使用兼容性好的中转地址
        url = "https://api.openai-proxy.com/v1/chat/completions"
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        resp_json = resp.json()
        
        if "choices" in resp_json:
            content = resp_json["choices"][0]["message"]["content"].strip()
            if "|||" in content:
                parts = content.split("|||")
                return parts[0].strip(), parts[1].strip()
            else:
                return content, "今天要开开心心的！"
    except Exception as e:
        print(f"GPT 请求失败: {e}")
        
    return "煤气早安！GitHub有点卡，但我想你不会卡❤️", "记得按时吃饭！"

def send_message():
    token = get_access_token()
    if not token: return

    # 1. 获取数据 (只获取一次，保证两个人生日收到的是同样的内容)
    weather, temp = get_weather()
    week_day = get_week_day_str()
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    msg_1, msg_2 = get_gpt_message(weather, temp, week_day)
    
    # 2. 循环发送给列表里的每一个人
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
