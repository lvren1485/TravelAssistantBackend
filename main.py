from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import services
import schemas
import config
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="智能旅行规划助手API",
    description="整合天气、地图、航班和大模型API的旅行规划后端服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件,允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"全局异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "服务器内部错误",
            "detail": str(exc)
        }
    )


@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "智能旅行规划助手API v1.0",
        "status": "running",
        "docs_url": "/docs",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "travel-assistant-api",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.post(
    "/api/generate_plan",
    response_model=schemas.TravelPlanResponse,
    responses={
        200: {"description": "成功生成旅行计划"},
        400: {"description": "请求参数错误"},
        500: {"description": "服务器内部错误"}
    }
)
async def generate_travel_plan(request: schemas.TravelRequest):
    """
    生成旅行规划的核心接口

    该接口整合了以下外部API服务:
    1. 天气API - 获取目的地天气预报
    2. 地图API - 获取景点信息(POI)
    3. 航班信息API - 获取航班数据(可选)
    4. 大语言模型API - 生成智能行程规划
    """
    logger.info(f"收到行程规划请求: {request.destination}, {request.days}天")

    try:
        # 验证输入
        if not request.destination or not request.destination.strip():
            raise HTTPException(status_code=400, detail="目的地不能为空")

        if request.days < 1 or request.days > 30:
            raise HTTPException(status_code=400, detail="旅行天数必须在1-30天之间")

        # 1. 获取天气信息
        logger.info(f"正在获取{request.destination}的天气信息...")
        weather_info = services.get_weather_info(request.destination)

        # 2. 获取景点信息
        logger.info(f"正在获取{request.destination}的景点信息...")
        attractions = services.get_attractions(request.destination)

        # 3. 获取航班信息
        flight_info = None
        if request.departure_city and request.start_date:
            logger.info(f"正在查询航班信息: {request.departure_city} -> {request.destination}")
            flight_info = services.get_flight_info(
                request.departure_city,
                request.destination,
                request.start_date
            )

        # 4. 调用大模型生成行程
        logger.info("正在生成智能行程规划...")
        itinerary = services.generate_itinerary_with_llm(
            destination=request.destination,
            days=request.days,
            budget=request.budget,
            weather=weather_info,
            attractions=attractions,
            interests=request.interests,
            start_date=request.start_date
        )

        # 5. 返回结构化响应
        response = schemas.TravelPlanResponse(
            destination=request.destination,
            itinerary=itinerary,
            weather_info=weather_info,
            attractions=attractions,
            flight_info=flight_info,
            status="success",
            message="行程规划生成成功"
        )

        logger.info(f"行程规划生成完成: {request.destination}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成行程时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"生成行程失败: {str(e)}"
        )


@app.get("/api/test/weather/{city}")
async def test_weather(city: str):
    """测试天气API接口"""
    try:
        weather = services.get_weather_info(city)
        return {
            "status": "success",
            "city": city,
            "weather": [w.dict() for w in weather]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/test/attractions/{city}")
async def test_attractions(city: str):
    """测试景点API接口"""
    try:
        attractions = services.get_attractions(city)
        return {
            "status": "success",
            "city": city,
            "attractions": [a.dict() for a in attractions]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/info")
async def api_info():
    """API信息接口"""
    return {
        "name": "智能旅行规划助手API",
        "version": "1.0.0",
        "description": "整合多个Web API的旅行规划服务",
        "integrated_apis": [
            {
                "name": "天气API",
                "purpose": "获取目的地天气预报",
                "provider": "QWeather"
            },
            {
                "name": "地图API",
                "purpose": "获取景点信息和地理数据",
                "provider": "高德地图"
            },
            {
                "name": "航班信息API",
                "purpose": "查询航班时刻和价格",
                "provider": "模拟数据(可替换为真实API)"
            },
            {
                "name": "OpenAI GPT API",
                "purpose": "生成智能旅行规划",
                "provider": "OpenAI"
            }
        ],
        "endpoints": [
            "/api/generate_plan - 生成旅行规划",
            "/api/test/weather/{city} - 测试天气API",
            "/api/test/attractions/{city} - 测试景点API",
            "/health - 健康检查",
            "/docs - API文档"
        ]
    }


@app.get("/api/test/flights")
async def test_flights(
        departure_city: str = "北京",
        destination: str = "上海",
        date: str = None
):
    """测试航班信息API接口"""
    try:
        # 如果没有提供日期，使用明天的日期
        if not date:
            from datetime import datetime, timedelta
            tomorrow = datetime.now() + timedelta(days=1)
            date = tomorrow.strftime("%Y-%m-%d")

        # 验证日期格式
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="日期格式错误，请使用 YYYY-MM-DD 格式"
            )

        logger.info(f"测试航班查询: {departure_city} -> {destination} on {date}")

        # 获取航班信息
        flights = services.get_flight_info(departure_city, destination, date)

        return {
            "status": "success",
            "query": {
                "departure_city": departure_city,
                "destination": destination,
                "date": date
            },
            "flight_count": len(flights),
            "flights": [flight.dict() for flight in flights],
            "summary": {
                "cheapest": min([int(f.price[1:]) for f in flights]) if flights else 0,
                "most_expensive": max([int(f.price[1:]) for f in flights]) if flights else 0,
                "airlines": list(set([f.airline for f in flights])),
                "direct_flights": len([f for f in flights if f.transfer == "直飞"])
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"测试航班API时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"航班查询失败: {str(e)}"
        )


@app.get("/api/test/flights/airlines")
async def test_airlines_info():
    """获取支持的航空公司信息"""
    return {
        "status": "success",
        "supported_airlines": [
            {
                "code": "CA",
                "name": "中国国际航空",
                "type": "全服务航空"
            },
            {
                "code": "MU",
                "name": "东方航空",
                "type": "全服务航空"
            },
            {
                "code": "CZ",
                "name": "南方航空",
                "type": "全服务航空"
            },
            {
                "code": "HU",
                "name": "海南航空",
                "type": "全服务航空"
            },
            {
                "code": "ZH",
                "name": "深圳航空",
                "type": "全服务航空"
            },
            {
                "code": "MF",
                "name": "厦门航空",
                "type": "全服务航空"
            },
            {
                "code": "9C",
                "name": "春秋航空",
                "type": "廉价航空"
            },
            {
                "code": "KN",
                "name": "中国联合航空",
                "type": "廉价航空"
            }
        ],
        "total_airlines": 8,
        "note": "当前为模拟数据，实际支持的航空公司可能更多"
    }


@app.get("/api/test/flights/routes")
async def test_popular_routes():
    """获取热门航线信息"""
    popular_routes = [
        {
            "route": "北京 - 上海",
            "duration": "2h-2.5h",
            "frequency": "高频",
            "typical_price": "¥400-¥1200",
            "description": "京沪快线，航班密集"
        },
        {
            "route": "上海 - 广州",
            "duration": "2h15m-2h45m",
            "frequency": "高频",
            "typical_price": "¥500-¥1500",
            "description": "华东华南主要航线"
        },
        {
            "route": "北京 - 广州",
            "duration": "3h-3.5h",
            "frequency": "中高频",
            "typical_price": "¥600-¥1800",
            "description": "南北干线"
        },
        {
            "route": "深圳 - 北京",
            "duration": "3h-3.5h",
            "frequency": "中高频",
            "typical_price": "¥550-¥1600",
            "description": "商务热门航线"
        },
        {
            "route": "成都 - 上海",
            "duration": "2.5h-3h",
            "frequency": "中频",
            "typical_price": "¥450-¥1400",
            "description": "西南华东重要航线"
        }
    ]

    return {
        "status": "success",
        "popular_routes": popular_routes,
        "total_routes": len(popular_routes),
        "note": "以上为常见航线参考信息"
    }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )