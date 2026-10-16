# AI Construction Estimator & Quiz Engine

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688.svg)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-orange.svg)](https://openai.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Автоматизированный микросервис для строительных компаний: интерактивный квиз-опросник, валидация параметров, детерминированный расчёт строительных объёмов и многоступенчатая генерация сметной документации с помощью LLM (Chain-of-Thought) без галлюцинаций.

---

## 🏗 Архитектура многоступенчатого пайплайна (Chain-of-Thought)

Нейросеть не считает объёмы стройматериалов напрямую (во избежание арифметических ошибок и выдуманных цен). Расчёт разделён на изолированные шаги:

```
[Пользовательский квиз] 
         │ 
         ▼
[1. Валидация схемы (Pydantic)] ───► Отсечение некорректных размеров и параметров
         │
         ▼
[2. Детерминированный калькулятор] ──► Строгие формулы расчёта бетона, блоков, арматуры и кровли
         │
         ▼
[3. LLM Prompt Engine (Chain-of-Thought)]
  ├─ Шаг A: Экспертный аудит спецификации материалов
  ├─ Шаг B: Формирование рекомендаций по монтажу и этапам
  └─ Шаг C: Генерация коммерческого предложения / сметы
         │
         ▼
[4. Сборка PDF & ЮKassa API] ───► Превью для клиента + Полная смета после оплаты
```

---

## ⚡ Ключевой функционал

- **Интерактивный квиз**: сбор вводных данных (тип фундамента, площадь, этажность, материал стен, кровля).
- **Математический модуль**: формульный расчёт кубатуры бетона, количества газобетонных/кирпичных блоков, площади кровельного покрытия с учётом коэффициентов запаса (5-10%).
- **Multi-step AI Engine**: системные промпты с ролевой моделью сметчика-инженера и строгим JSON/Markdown-выводом.
- **Интеграция платежей**: создание счетов через ЮKassa / СБП для выдачи расширенных смет.
- **FastAPI REST API**: готово к встраиванию в любой фронтенд (React, Vue, чистый JS/HTML) или Telegram-бота.

---

## 🚀 Быстрый старт

### 1. Клонирование и установка зависимостей
```bash
git clone https://github.com/your-username/ai-construction-estimator.git
cd ai-construction-estimator
python -m venv venv
source venv/bin/activate  # на Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Настройка переменных окружения
Создайте файл `.env`:
```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
PORT=8000
```

### 3. Запуск сервера
```bash
uvicorn main:app --reload --port 8000
```
Документация Swagger UI доступна по адресу: `http://localhost:8000/docs`

---

## 📡 Примеры API

### POST `/api/v1/estimate`
Тело запроса:
```json
{
  "building_type": "residential_house",
  "floors": 2,
  "area_sq_m": 150.0,
  "wall_material": "aerated_concrete",
  "foundation_type": "monolithic_slab",
  "roof_type": "metal_tile"
}
```

Ответ сервиса:
```json
{
  "status": "success",
  "raw_calculations": {
    "concrete_volume_m3": 45.0,
    "wall_blocks_m3": 54.0,
    "rebar_tons": 3.6,
    "estimated_rough_cost_rub": 3850000
  },
  "ai_analysis": "### Экспертное заключение по смете...",
  "pdf_download_url": "/api/v1/download/estimate_abc123.pdf"
}
```

---

## 📄 Лицензия
MIT License. Проект открыт для коммерческого и учебного использования.
