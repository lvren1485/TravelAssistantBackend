import os
from dotenv import load_dotenv

# 加载环境变量文件(如果存在)
load_dotenv()

# 天气API配置
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "天气API密钥")
WEATHER_API_URL = "http://apis.juhe.cn/simpleWeather/query"

# 地图API配置
MAP_API_KEY = os.getenv("MAP_API_KEY", "景点API密钥")
MAP_API_URL = "http://apis.juhe.cn/fapigx/scenic/query"

# 航班API配置 - 模拟航班数据(可替换为真实API如携程、飞常准等)
FLIGHT_API_KEY = os.getenv("FLIGHT_API_KEY", "航班API密钥")
FLIGHT_API_URL = "https://api.example.com/flights"  # 示例URL,需替换

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "Deepseek API密钥")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# 其他配置
TIMEOUT = 10  # 请求超时时间(秒)
MAX_ATTRACTIONS = 6  # 最多返回的景点数量

# CORS配置
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite默认端口
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]