"""
API Simulada - Data Driven API
Simula endpoints de consulta de sensores e consumo energético
"""
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import random
import uvicorn

app = FastAPI(
    title="Data Driven API - Simulada",
    description="API simulada para consulta de dados de sensores energéticos",
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


# ========== MODELS ==========

class SensorBase(BaseModel):
    sensor_id: str
    sensor_name: str
    location: str
    status: str
    last_reading: datetime


class ConsumptionData(BaseModel):
    sensor_id: str
    sensor_name: str
    location: str
    period: str
    consumption_kwh: float
    status: str
    last_reading: datetime
    average_hourly_kwh: float
    peak_consumption_kwh: float
    off_peak_consumption_kwh: float


class SensorListResponse(BaseModel):
    success: bool
    total: int
    sensors: List[SensorBase]


class ConsumptionResponse(BaseModel):
    success: bool
    data: ConsumptionData


# ========== DATABASE SIMULADO ==========

SENSORS_DB = {
    "SENSOR_001": {
        "sensor_name": "Sensor Refrigeração - Câmara Fria A",
        "location": "Câmara Fria - Setor A",
        "status": "online",
        "type": "refrigeration"
    },
    "SENSOR_002": {
        "sensor_name": "Sensor Refrigeração - Câmara Fria B",
        "location": "Câmara Fria - Setor B",
        "status": "online",
        "type": "refrigeration"
    },
    "SENSOR_003": {
        "sensor_name": "Sensor HVAC - Escritório Principal",
        "location": "Escritório - 2º Andar",
        "status": "online",
        "type": "hvac"
    },
    "SENSOR_004": {
        "sensor_name": "Sensor Iluminação - Galpão Industrial",
        "location": "Galpão - Setor C",
        "status": "maintenance",
        "type": "lighting"
    },
    "SENSOR_005": {
        "sensor_name": "Sensor Refrigeração - Túnel de Congelamento",
        "location": "Túnel de Congelamento - Setor D",
        "status": "online",
        "type": "refrigeration"
    }
}

# Dados base de consumo por período (kWh)
CONSUMPTION_BASE = {
    "hora": (10.0, 15.0),
    "dia": (250.0, 350.0),
    "semana": (1800.0, 2200.0),
    "mes": (7500.0, 9500.0)
}


# ========== HELPER FUNCTIONS ==========

def verify_token(authorization: Optional[str] = Header(None)):
    """Verifica token de autenticação (simplificado para POC)"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Token não fornecido")
    
    # Para a POC, aceita qualquer token que comece com "Bearer "
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Formato de token inválido")
    
    return True


def generate_consumption_data(sensor_id: str, period: str) -> dict:
    """Gera dados de consumo simulados para um sensor"""
    
    if sensor_id not in SENSORS_DB:
        return None
    
    sensor_info = SENSORS_DB[sensor_id]
    
    # Gera consumo base com variação aleatória
    base_min, base_max = CONSUMPTION_BASE.get(period, (0, 0))
    consumption = round(random.uniform(base_min, base_max), 2)
    
    # Calcula métricas derivadas
    hours_map = {"hora": 1, "dia": 24, "semana": 168, "mes": 720}
    hours = hours_map.get(period, 1)
    
    avg_hourly = round(consumption / hours, 2)
    peak = round(avg_hourly * 1.4, 2)  # 40% acima da média
    off_peak = round(avg_hourly * 0.7, 2)  # 30% abaixo da média
    
    return {
        "sensor_id": sensor_id,
        "sensor_name": sensor_info["sensor_name"],
        "location": sensor_info["location"],
        "period": period,
        "consumption_kwh": consumption,
        "status": sensor_info["status"],
        "last_reading": datetime.now() - timedelta(minutes=random.randint(1, 30)),
        "average_hourly_kwh": avg_hourly,
        "peak_consumption_kwh": peak,
        "off_peak_consumption_kwh": off_peak
    }


# ========== ENDPOINTS ==========

@app.get("/")
def root():
    """Endpoint raiz"""
    return {
        "message": "Data Driven API - Simulada",
        "version": "1.0.0",
        "endpoints": {
            "sensors": "/api/sensors",
            "consumption": "/api/sensors/{sensor_id}/consumption"
        }
    }


@app.get("/api/sensors", response_model=SensorListResponse)
def list_sensors(authorization: str = Header(None)):
    """Lista todos os sensores disponíveis"""
    verify_token(authorization)
    
    sensors = [
        {
            "sensor_id": sensor_id,
            "sensor_name": info["sensor_name"],
            "location": info["location"],
            "status": info["status"],
            "last_reading": datetime.now() - timedelta(minutes=random.randint(1, 30))
        }
        for sensor_id, info in SENSORS_DB.items()
    ]
    
    return {
        "success": True,
        "total": len(sensors),
        "sensors": sensors
    }


@app.get("/api/sensors/{sensor_id}/consumption", response_model=ConsumptionResponse)
def get_sensor_consumption(
    sensor_id: str,
    period: str = "hora",
    authorization: str = Header(None)
):
    """
    Consulta o consumo de energia de um sensor específico
    
    Args:
        sensor_id: ID do sensor (ex: SENSOR_001)
        period: Período de análise (hora, dia, semana, mes)
    """
    verify_token(authorization)
    
    # Valida período
    if period not in ["hora", "dia", "semana", "mes"]:
        raise HTTPException(
            status_code=400,
            detail="Período inválido. Use: hora, dia, semana ou mes"
        )
    
    # Gera dados de consumo
    consumption_data = generate_consumption_data(sensor_id, period)
    
    if not consumption_data:
        raise HTTPException(
            status_code=404,
            detail=f"Sensor {sensor_id} não encontrado"
        )
    
    return {
        "success": True,
        "data": consumption_data
    }


@app.get("/api/sensors/{sensor_id}")
def get_sensor_info(sensor_id: str, authorization: str = Header(None)):
    """Obtém informações de um sensor específico"""
    verify_token(authorization)
    
    if sensor_id not in SENSORS_DB:
        raise HTTPException(
            status_code=404,
            detail=f"Sensor {sensor_id} não encontrado"
        )
    
    sensor_info = SENSORS_DB[sensor_id]
    
    return {
        "success": True,
        "data": {
            "sensor_id": sensor_id,
            "sensor_name": sensor_info["sensor_name"],
            "location": sensor_info["location"],
            "status": sensor_info["status"],
            "type": sensor_info["type"],
            "last_reading": datetime.now() - timedelta(minutes=random.randint(1, 30))
        }
    }


@app.get("/health")
def health_check():
    """Health check do serviço"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "total_sensors": len(SENSORS_DB)
    }


if __name__ == "__main__":
    print("🚀 Iniciando Data Driven API Simulada...")
    print("📡 Servidor rodando em: http://localhost:8000")
    print("📖 Documentação: http://localhost:8000/docs")
    print("🔍 Sensores disponíveis:", list(SENSORS_DB.keys()))
    print("\n✨ Use Ctrl+C para parar o servidor\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
