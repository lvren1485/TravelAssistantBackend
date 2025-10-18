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
    1. 和风天气API - 获取目的地天气预报
    2. 高德地图API - 获取景点信息(POI)
    3. 航班信息API - 获取航班数据(可选)
    4. OpenAI/大模型API - 生成智能行程规划
    """
    logger.info(f"收到行程规划请求: {request.destination}, {request.days}天")

    try:
        # 验证输入
        if not request.destination or not request.destination.strip():
            raise HTTPException(status_code=400, detail="目的地不能为空")

        if request.days < 1 or request.days > 30:
            raise HTTPException(status_code=400, detail="旅行天数必须在1-30天之间")

        # 1. 获取天气信息(API 1: 和风天气)
        logger.info(f"正在获取{request.destination}的天气信息...")
        weather_info = services.get_weather_info(request.destination)

        # 2. 获取景点信息(API 2: 高德地图)
        logger.info(f"正在获取{request.destination}的景点信息...")
        attractions = services.get_attractions(request.destination)

        # 3. 获取航班信息(API 3: 航班信息API - 可选)
        flight_info = None
        if request.departure_city and request.start_date:
            logger.info(f"正在查询航班信息: {request.departure_city} -> {request.destination}")
            flight_info = services.get_flight_info(
                request.departure_city,
                request.destination,
                request.start_date
            )

        # 4. 调用大模型生成行程(API 4: OpenAI/大模型)
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )