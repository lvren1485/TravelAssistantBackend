import requests
import config
import json
from typing import List, Dict
from schemas import WeatherInfo, Attraction, FlightInfo
import random


def get_city_location(city: str) -> Dict:
    """获取城市的地理位置信息(经纬度) - 保留原函数，可能在其他地方使用"""
    try:
        # 使用和风天气的城市查询API
        params = {
            "key": config.WEATHER_API_KEY,
            "location": city,
            "adm": "中国"
        }
        response = requests.get(config.WEATHER_GEO_URL, params=params, timeout=config.TIMEOUT)
        response.raise_for_status()
        data = response.json()

        if data.get("code") == "200" and data.get("location"):
            location = data["location"][0]
            return {
                "id": location.get("id"),
                "name": location.get("name"),
                "lat": location.get("lat"),
                "lon": location.get("lon")
            }
        return None
    except Exception as e:
        print(f"城市位置查询失败: {e}")
        return None


def get_weather_info(city: str) -> List[WeatherInfo]:
    """获取未来3天天气信息 - 使用聚合数据API"""
    try:
        params = {
            "key": config.WEATHER_API_KEY,  # 需要在config中配置聚合数据的API KEY
            "city": city
        }

        response = requests.get(
            config.WEATHER_API_URL,
            params=params,
            timeout=config.TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        print(data)

        weather_list = []

        # 检查API返回状态
        if data.get("error_code") == 0 and data.get("result"):
            result = data["result"]

            # 获取未来天气信息
            future_weather = result.get("future", [])[:4]  # 只取前4天

            for day in future_weather:
                # 解析温度范围 "1/7℃" -> 最高温7°C, 最低温1°C
                temp_range = day.get("temperature", "N/A").replace("℃", "")
                if "/" in temp_range and temp_range != "N/A":
                    temp_parts = temp_range.split("/")
                    night_temp = f"{temp_parts[0]}°C" if len(temp_parts) > 0 else "N/A"
                    day_temp = f"{temp_parts[1]}°C" if len(temp_parts) > 1 else "N/A"
                else:
                    night_temp = "N/A"
                    day_temp = "N/A"

                # 解析天气情况 "小雨转多云" -> 白天小雨, 夜间多云
                weather_text = day.get("weather", "未知")
                if "转" in weather_text:
                    weather_parts = weather_text.split("转")
                    day_weather = weather_parts[0] if len(weather_parts) > 0 else "未知"
                    night_weather = weather_parts[1] if len(weather_parts) > 1 else "未知"
                else:
                    day_weather = weather_text
                    night_weather = weather_text

                weather_list.append(WeatherInfo(
                    date=day.get("date", ""),
                    day_temp=day_temp,
                    night_temp=night_temp,
                    day_weather=day_weather,
                    night_weather=night_weather,
                    wind=day.get("direct", "N/A")
                ))

        return weather_list if weather_list else [
            WeatherInfo(
                date="N/A",
                day_temp="N/A",
                night_temp="N/A",
                day_weather="数据获取失败",
                night_weather="数据获取失败",
                wind="N/A"
            )
        ]
    except Exception as e:
        print(f"天气API请求失败: {e}")
        return [WeatherInfo(
            date="N/A",
            day_temp="N/A",
            night_temp="N/A",
            day_weather="服务暂不可用",
            night_weather="服务暂不可用",
            wind="N/A"
        )]


def get_attractions(city: str) -> List[Attraction]:
    """获取景点信息 - 使用聚合数据景区查询API"""
    try:
        params = {
            "key": config.MAP_API_KEY,  # 需要在config中配置聚合数据的API KEY
            "word": city,
            "city": city,
            "num": config.MAX_ATTRACTIONS  # 返回数量，建议在config中设置
        }

        response = requests.get(
            config.MAP_API_URL,
            params=params,
            timeout=config.TIMEOUT
        )
        response.raise_for_status()
        data = response.json()

        attractions = []

        # 检查API返回状态
        if data.get("error_code") == 0 and data.get("result"):
            result = data["result"]
            scenic_list = result.get("list", [])

            for scenic in scenic_list:
                # 处理景点内容，去除HTML标签和多余空格
                content = scenic.get("content", "")
                if content:
                    # 简单清理HTML标签
                    content = content.replace("<br>", " ").replace("    ", " ")
                    # 截取前100字符作为简介
                    content = content[:100] + "..." if len(content) > 100 else content

                attractions.append(Attraction(
                    name=scenic.get("name", ""),
                    address=f"{scenic.get('province', '')}{scenic.get('city', '')}",
                    type="风景名胜",  # 聚合数据API没有直接提供类型，可以设为固定值或从内容推断
                    description=content  # 可能需要修改schemas.py添加description字段
                ))

        return attractions if attractions else [
            Attraction(name="景点信息暂不可用", address="", type="", description="")
        ]
    except Exception as e:
        print(f"景点API请求失败: {e}")
        return [Attraction(name="景点信息获取失败", address="", type="", description="")]


def get_flight_info(departure_city: str, destination: str, date: str) -> List[FlightInfo]:
    """获取航班信息(模拟数据,可替换为真实API)"""
    try:
        # 这里使用模拟数据,实际项目中应该调用真实的航班API
        # 如:携程API、飞常准API、航旅纵横API等

        # 模拟航班数据
        mock_flights = [
            FlightInfo(
                flight_number=f"{random.choice(['CA', 'MU', 'CZ'])}{random.randint(1000, 9999)}",
                departure_time=f"{random.randint(6, 22):02d}:{random.choice(['00', '30'])}",
                arrival_time=f"{random.randint(8, 23):02d}:{random.choice(['00', '30'])}",
                price=f"¥{random.randint(500, 2000)}",
                airline=random.choice(["中国国际航空", "东方航空", "南方航空"])
            )
            for _ in range(3)
        ]

        return mock_flights
    except Exception as e:
        print(f"航班API请求失败: {e}")
        return []


"内容无需特别精细，但要求全面。计划尽量控制在500字以内。"

def generate_itinerary_with_llm(
        destination: str,
        days: int,
        budget: str,
        weather: List[WeatherInfo],
        attractions: List[Attraction],
        interests: List[str] = None,
        start_date: str = None
) -> str:
    """调用大模型生成行程规划"""
    try:
        # 构建结构化的提示词
        weather_summary = "\n".join([
            f"- {w.date}: 白天{w.day_temp}/{w.day_weather}, 夜间{w.night_temp}/{w.night_weather}, {w.wind}"
            for w in weather[:days]
        ])

        attraction_list = "\n".join([
            f"- {a.name} ({a.type}): {a.address}"
            for a in attractions[:8]
        ])

        interests_text = "、".join(interests) if interests else "常规观光"

        prompt = f"""你是一位专业的旅行规划师。请为用户制定一份{destination}{days}天旅行计划。

**用户需求:**
- 目的地: {destination}
- 旅行天数: {days}天
- 预算: {budget}
- 出发日期: {start_date if start_date else '待定'}
- 兴趣偏好: {interests_text}

**天气信息:**
{weather_summary}

**推荐景点:**
{attraction_list}

**要求:**
1. 按天组织行程,每天包含上午、下午和晚上的具体活动
2. 结合天气情况安排合适的活动(如雨天安排室内景点)
3. 根据景点位置合理规划路线,减少往返
4. 考虑用户的兴趣偏好,突出相关景点
5. 包含实用建议(如交通方式、餐饮推荐、注意事项)
6. 根据预算水平推荐合适的住宿和餐饮档次
7. 使用Markdown格式,结构清晰,易于阅读

请生成详细、实用且个性化的旅行规划。"""

        headers = {
            "Authorization": f"Bearer {config.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": config.DEEPSEEK_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位经验丰富的旅行规划专家,擅长根据天气、景点、用户偏好等信息制定详细的旅行计划。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 4000,
            "stream": False
        }

        response = requests.post(
            config.DEEPSEEK_API_URL,
            headers=headers,
            json=data,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()

        # DeepSeek API返回格式
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            print(f"DeepSeek API返回格式异常: {result}")
            return generate_fallback_itinerary(destination, days, weather, attractions)

    except requests.exceptions.Timeout:
        print("DeepSeek API调用超时")
        return generate_fallback_itinerary(destination, days, weather, attractions)
    except requests.exceptions.RequestException as e:
        print(f"DeepSeek API网络请求失败: {e}")
        return generate_fallback_itinerary(destination, days, weather, attractions)
    except Exception as e:
        print(f"DeepSeek API调用失败: {e}")
        return generate_fallback_itinerary(destination, days, weather, attractions)


def generate_fallback_itinerary(
        destination: str,
        days: int,
        weather: List[WeatherInfo],
        attractions: List[Attraction]
) -> str:
    """生成备用行程(当LLM API失败时使用)"""
    itinerary = f"# {destination} {days}天旅行计划\n\n"
    itinerary += "*(由于智能规划服务暂时不可用,以下为基础行程建议)*\n\n"

    for day in range(1, days + 1):
        itinerary += f"## 第{day}天\n\n"
        if day <= len(weather):
            w = weather[day - 1]
            itinerary += f"**天气:** {w.day_weather}, {w.day_temp}\n\n"

        # 每天推荐2-3个景点
        day_attractions = attractions[(day - 1) * 2:day * 2 + 1]
        if day_attractions:
            itinerary += "**推荐景点:**\n"
            for attr in day_attractions:
                itinerary += f"- {attr.name}\n"
        itinerary += "\n"

    itinerary += "\n**温馨提示:** 建议根据实际情况调整行程,注意天气变化。\n"
    return itinerary