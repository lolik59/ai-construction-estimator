import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Literal

from calculator import ConstructionCalculator
from ai_engine import AIEstimateEngine

app = FastAPI(
    title="AI Construction Estimator API",
    description="Микросервис многоступенчатого расчета строительных смет с использованием ИИ",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EstimateRequest(BaseModel):
    building_type: str = Field(default="Загородный дом", description="Тип строения")
    area_sq_m: float = Field(gt=20, lt=2000, description="Общая площадь объекта, м²")
    floors: int = Field(ge=1, le=4, default=1, description="Количество этажей")
    wall_material: Literal["aerated_concrete", "brick"] = Field(default="aerated_concrete", description="Материал стен")
    foundation_type: Literal["monolithic_slab", "strip_foundation"] = Field(default="monolithic_slab", description="Тип фундамента")
    roof_type: Literal["metal_tile", "soft_roof"] = Field(default="metal_tile", description="Материал кровли")

class PaymentIntentRequest(BaseModel):
    estimate_id: str
    amount_rub: int = 490
    client_email: str

@app.post("/api/v1/estimate", summary="Расчёт сметы и AI-аудит")
async def calculate_estimate(data: EstimateRequest):
    # 1. Точный формульный расчёт
    calc_results = ConstructionCalculator.calculate(
        area_sq_m=data.area_sq_m,
        floors=data.floors,
        wall_material=data.wall_material,
        foundation_type=data.foundation_type,
        roof_type=data.roof_type
    )

    # 2. Многоступенчатая генерация аналитического отчёта
    ai_report = await AIEstimateEngine.generate_explanation(
        user_inputs=data.model_dump(),
        calc_results=calc_results
    )

    return {
        "status": "success",
        "input_summary": data.model_dump(),
        "calculations": calc_results,
        "ai_report_markdown": ai_report,
        "preview_features": [
            "Базовый расчёт материалов включён",
            "Детализированный график оплат доступен в полной смете",
            "Технологическая карта привязки к смете доступна после оплаты"
        ]
    }

@app.post("/api/v1/payments/create-intent", summary="Создание сессии оплаты (ЮKassa / СБП)")
async def create_payment_intent(data: PaymentIntentRequest):
    """
    Эмуляция создания платежной ссылки для шлюза ЮKassa / Robokassa
    """
    return {
        "payment_id": f"pay_{os.urandom(8).hex()}",
        "confirmation_url": f"https://yookassa.ru/checkout?orderId={data.estimate_id}",
        "amount": data.amount_rub,
        "currency": "RUB",
        "status": "pending"
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ai-construction-estimator"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
