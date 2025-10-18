import requests
import config
import json
from typing import List, Dict
from schemas import WeatherInfo, Attraction, FlightInfo
import random
from datetime import datetime, timedelta
from typing import List

def get_weather_info(city: str) -> List[WeatherInfo]:
    """获取未来4天天气信息 - 使用聚合数据API"""
    try:
        params = {
            "key": config.WEATHER_API_KEY,
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
            "key": config.MAP_API_KEY,
            "word": city,
            "city": city,
            "num": config.MAX_ATTRACTIONS  # 返回数量
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
            scenic_list = result.get("list", [])[:config.MAX_ATTRACTIONS] # 只取若干项

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
        # 航空公司代码和名称映射
        airlines = {
            "CA": "中国国际航空",
            "MU": "东方航空",
            "CZ": "南方航空",
            "HU": "海南航空",
            "ZH": "深圳航空",
            "MF": "厦门航空",
            "9C": "春秋航空",
            "KN": "中国联合航空"
        }

        # 常见机型
        aircraft_types = ["B737", "A320", "A321", "B787", "A330", "B777", "A350"]

        # 根据距离生成合理的飞行时长（分钟）
        city_pairs = {
            ("北京", "上海"): 120, ("上海", "广州"): 135, ("北京", "广州"): 180,
            ("深圳", "北京"): 185, ("成都", "上海"): 150, ("杭州", "广州"): 125
        }

        # 计算基础飞行时间
        base_duration = city_pairs.get((departure_city, destination), random.randint(90, 180))

        # 生成不同时间段的航班
        time_slots = [
            ("06:00", "08:00"),  # 早班
            ("09:00", "12:00"),  # 上午
            ("13:00", "16:00"),  # 下午
            ("17:00", "20:00"),  # 傍晚
            ("21:00", "23:00")  # 晚班
        ]

        mock_flights = []

        for i in range(random.randint(4, 8)):  # 生成4-8个航班
            airline_code, airline_name = random.choice(list(airlines.items()))

            # 选择时间段
            dep_slot = random.choice(time_slots)
            dep_hour = random.randint(int(dep_slot[0][:2]), int(dep_slot[1][:2]))
            dep_minute = random.choice(["00", "10", "20", "30", "40", "50"])
            departure_time = f"{dep_hour:02d}:{dep_minute}"

            # 计算到达时间
            dep_datetime = datetime.strptime(departure_time, "%H:%M")
            arr_datetime = dep_datetime + timedelta(minutes=base_duration + random.randint(-10, 30))
            arrival_time = arr_datetime.strftime("%H:%M")

            # 计算飞行时长
            duration_minutes = int((arr_datetime - dep_datetime).total_seconds() / 60)
            duration_str = f"{duration_minutes // 60}h{duration_minutes % 60:02d}m"

            # 生成价格（考虑时间段、航空公司等因素）
            base_price = 800
            if dep_slot[0] == "06:00":  # 早班便宜
                base_price -= 100
            elif dep_slot[0] == "21:00":  # 晚班便宜
                base_price -= 150
            else:  # 黄金时段贵
                base_price += 200

            if airline_code in ["9C", "KN"]:  # 廉价航空
                base_price -= 300

            final_price = max(400, base_price + random.randint(-100, 200))

            # 舱位类型
            seat_classes = ["经济舱", "超级经济舱", "商务舱", "头等舱"]
            seat_weights = [70, 15, 10, 5]  # 权重

            # 折扣信息
            discounts = ["", "学生价95折", "会员优惠", "限时特惠", "往返立减"]

            mock_flights.append(FlightInfo(
                flight_number=f"{airline_code}{random.randint(1300, 8999)}",
                departure_time=departure_time,
                arrival_time=arrival_time,
                price=f"¥{final_price}",
                airline=airline_name,
                aircraft_type=random.choice(aircraft_types),
                duration=duration_str,
                punctuality_rate=f"{random.randint(75, 95)}%",
                seat_class=random.choices(seat_classes, weights=seat_weights)[0],
                transfer="经停" if random.random() < 0.2 else "直飞",
                discount=random.choice(discounts) if random.random() < 0.3 else ""
            ))

        # 按价格排序
        mock_flights.sort(key=lambda x: int(x.price[1:]))

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

        prompt = f"""你是一位专业的旅行规划师。请为用户制定一份{destination}{days}天旅行计划。内容无需特别精细，但要求全面。计划尽量控制在600字以内。

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