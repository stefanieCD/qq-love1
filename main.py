import requests
import datetime
import os
import sys

# ==========================================
# 🛠 调试模式
# ==========================================
try:
    APP_ID = os.environ["APP_ID"]
    APP_SECRET = os.environ["APP_SECRET"]
    TEMPLATE_ID = os.environ["TEMPLATE_ID"]
except KeyError:
    print("❌ 错误：Secrets 变量缺失！")
    sys.exit(1)

# 👥 接收人列表
USERS = [
    "o13257d7f-0B3aLMx8UGIAaGZkUY",
    "o13257XIz2XpWkacUw08fny0mNyE"
]

CITY = "深圳"
# ==========================================

def get_access_token():
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APP_ID}&secret={APP_SECRET}"
    try:
        resp = requests.get(url).json()
        return resp.get('access_token')
    except:
        return None

def send_debug_message():
    token = get_access_token()
    if not token: 
        print("❌ Token 获取失败")
        return

    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # 🔥 强制写死内容，测试能不能显示
    msg_1 = "这是测试情话：我爱你"
    msg_2 = "这是测试建议：记得喝水"
    
    for user_id in USERS:
        print(f"正在发送给: {user_id} ...")
        url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={token}"
        
        data = {
            "touser": user_id,
            "template_id": TEMPLATE_ID,
            "data": {
                "date": {"value": today_date, "color": "#FF69B4"},
                "city": {"value": CITY, "color": "#173177"},
                "weather": {"value": "晴天", "color": "#FFA500"},
                "temperature": {"value": "25度", "color": "#00CC00"},
                # 这里的 key 必须和网页模板里的 {{xxxx.DATA}} 一样
                "love_msg": {"value": msg_1, "color": "#FF1493"},
                "suggestion": {"value": msg_2, "color": "#9370DB"}
            }
        }
        
        resp = requests.post(url, json=data).json()
        print(f"结果: {resp}")

if __name__ == "__main__":
    send_debug_message()
