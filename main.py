import requests
import datetime
import os
import sys

# ==========================================
# ☁️ 配置区
# ==========================================

# 1. 模板 ID (已更新为你提供的 ID)
# 优先从环境变量获取，如果获取不到，则使用默认值
TEMPLATE_ID = os.environ.get("TEMPLATE_ID", "-yHfo5HM4Rn2OTBDgMDYgapaL4-GxReRRyPzGLVxriE")

# 2. 敏感信息 (必须在 GitHub Secrets 中设置)
try:
    APP_ID = os.environ["APP_ID"]
    APP_SECRET = os.environ["APP_SECRET"]
    # 如果没有设置 GPT_KEY，脚本会自动使用默认情话
    GPT_API_KEY = os.environ.get("GPT_API_KEY") 
except KeyError:
    print("❌ 错误：APP_ID 或 APP_SECRET 缺失！请检查 GitHub Actions Secrets 配置。")
    sys.exit(1)

# 3. 用户列表 (这里填你和你女朋友的微信号 OpenID)
USERS = [
    "o13257d7f-0B3aLMx8UGIAaGZkUY", 
    "o13257XIz2XpWkacUw08fny0mNyE"
]

# 4. 其他配置
CITY = "深圳"
CLICK_URL = "https://tianqi.qq.com/index.htm"

# ==========================================

def get_access_token():
    """获取微信 Access Token"""
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APP_ID}&secret={APP_SECRET}"
    try:
        resp = requests.get(url).json()
        return resp.get('access_token')
    except Exception as e:
        print(f"Token 获取失败: {e}")
        return None

def get_weather_data():
    """
    获取天气数据，并拆分为天气状况和温度
    返回字典: {'weather': '晴', 'temp': '20~25℃'}
    """
    default_data = {"weather": "晴", "temp": "25℃"}
    try:
        url = f"http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city={CITY}"
        res = requests.get(url).json()
        if res and res['data'] and res['data']['list']:
            today = res['data']['list'][0]
            # 提取具体数据
            weather_status = today['weather']
            low = today['low']
            high = today['high']
            return {
                "weather": weather_status,
                "temp": f"{low} ~ {high}℃"
            }
    except Exception as e:
        print(f"天气获取失败: {e}")
    return default_data

def get_gpt_message():
    """
    获取 GPT 生成的情话和建议
    """
    # 如果没有 Key，直接返回默认的土味情话，防止报错
    if not GPT_API_KEY:
        print("⚠️ 未检测到 GPT_API_KEY，将发送默认文案。")
        return "今天也是爱琪琪的一天！", "记得按时吃饭，多喝水哦"
    
    prompt = "请生成两句话，用|||隔开。第一句是给女朋友琪琪的超甜早安情话（20字内），第二句是幽默温馨的今日建议（15字内）。"
    
    headers = {"Authorization": f"Bearer {GPT_API_KEY}"}
    data = {
        "model": "gpt-4o-mini", 
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        # 注意：如果你在 GitHub Actions (海外环境) 运行，可以直接用 api.openai.com
        # 如果在国内服务器运行，请保持 api.openai-proxy.com
        url = "https://api.openai-proxy.com/v1/chat/completions"
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        
        if resp.status_code != 200:
            print(f"GPT 请求失败: {resp.text}")
            return "李杨最爱琪琪！", "今天要开开心心"

        content = resp.json()["choices"][0]["message"]["content"].strip()
        
        if "|||" in content:
            parts = content.split("|||")
            return parts[0].strip(), parts[1].strip()
        return content[:20], "今天要开心"
    except Exception as e:
        print(f"GPT Error: {e}")
        return "李杨最爱琪琪！(GPT累了)", "记得带伞或防晒"

def send_message():
    token = get_access_token()
    if not token:
        print("无法获取 Token，终止发送。")
        return

    # 1. 获取数据
    weather_data = get_weather_data()
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    week_day = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"][datetime.datetime.now().weekday()]
    msg_1, msg_2 = get_gpt_message()
    
    print(f"正在发送 -> 日期:{today_date} 天气:{weather_data['weather']} 情话:{msg_1}")
    print(f"使用模板 ID: {TEMPLATE_ID}")

    # 2. 构造发送请求
    for user_id in USERS:
        url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={token}"
        
        # 核心修改：这里的 Key 必须和你的微信后台模版 {{xxxx.DATA}} 完全一致
        payload = {
            "touser": user_id,
            "template_id": TEMPLATE_ID,
            "url": CLICK_URL,
            "data": {
                # 对应 {{date.DATA}}
                "date": {
                    "value": f"{today_date} {week_day}", 
                    "color": "#00BFFF" # 深天蓝
                },
                # 对应 {{city.DATA}}
                "city": {
                    "value": CITY, 
                    "color": "#808080" # 灰色
                },
                # 对应 {{weather.DATA}}
                "weather": {
                    "value": weather_data['weather'], 
                    "color": "#FFA500" # 橙色
                },
                # 对应 {{temperature.DATA}}
                "temperature": {
                    "value": weather_data['temp'], 
                    "color": "#FF6347" # 番茄红
                },
                # 对应 {{love_msg.DATA}}
                "love_msg": {
                    "value": msg_1, 
                    "color": "#FF1493" # 深粉色 (重点高亮)
                },
                # 对应 {{suggestion.DATA}}
                "suggestion": {
                    "value": msg_2, 
                    "color": "#32CD32" # 柠檬绿
                }
            }
        }
        
        resp = requests.post(url, json=payload).json()
        if resp.get("errcode") == 0:
            print(f"✅ 发送给 {user_id} 成功")
        else:
            print(f"❌ 发送给 {user_id} 失败: {resp}")

if __name__ == "__main__":
    send_message()
