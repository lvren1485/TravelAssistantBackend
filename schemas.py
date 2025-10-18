from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from dataclasses import dataclass


# 请求模型:定义前端发送的数据格式
class TravelRequest(BaseModel):
    destination: str = Field(..., description="目的地城市名称", example="北京")
    days: int = Field(..., ge=1, le=30, description="旅行天数", example=3)
    budget: str = Field(..., description="预算范围", example="中等")
    start_date: Optional[str] = Field(None, description="出发日期", example="2025-11-01")
    departure_city: Optional[str] = Field(None, description="出发城市", example="上海")
    interests: Optional[List[str]] = Field(
        default=None,
        description="兴趣偏好列表",
        example=["历史文化", "美食", "自然风光"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "destination": "北京",
                "days": 3,
                "budget": "中等",
                "start_date": "2025-11-01",
                "departure_city": "上海",
                "interests": ["历史文化", "美食"]
            }
        }


# 天气信息模型
class WeatherInfo(BaseModel):
    date: str
    day_temp: str
    night_temp: str
    day_weather: str
    night_weather: str
    wind: str


# 景点信息模型
class Attraction(BaseModel):
    name: str
    address: Optional[str] = None
    type: Optional[str] = None
    description: str = ""


# 航班信息模型
class FlightInfo(BaseModel):
    flight_number: str
    departure_time: str
    arrival_time: str
    price: str
    airline: str
    aircraft_type: Optional[str] = ""
    duration: Optional[str] = ""
    punctuality_rate: Optional[str] = ""
    seat_class: Optional[str] = ""
    transfer: Optional[str] = ""
    discount: Optional[str] = ""

    class Config:
        json_encoders = {
            # 如果有自定义类型的编码需求可以在这里添加
        }


# 响应模型:定义返回给前端的数据格式
class TravelPlanResponse(BaseModel):
    destination: str
    itinerary: str
    weather_info: List[WeatherInfo]
    attractions: List[Attraction]
    flight_info: Optional[List[FlightInfo]] = None
    status: str = "success"
    message: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "destination": "北京",
                "itinerary": "详细的3天行程规划...",
                "weather_info": [
                    {
                        "date": "2025-11-01",
                        "day_temp": "18°C",
                        "night_temp": "8°C",
                        "day_weather": "晴",
                        "night_weather": "晴",
                        "wind": "北风3-4级"
                    }
                ],
                "attractions": [
                    {
                        "name": "故宫博物院",
                        "address": "北京市东城区景山前街4号",
                        "type": "风景名胜"
                    }
                ],
                "status": "success"
            }
        }


# 错误响应模型
class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    detail: Optional[str] = None