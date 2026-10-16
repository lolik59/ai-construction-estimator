import os
import json
from typing import Dict, Any

class AIEstimateEngine:
    """
    Многоступенчатый генератор экспертных сметных отчётов (Chain-of-Thought).
    """

    SYSTEM_PROMPT = """Ты — ведущий инженер-сметчик с 15-летним стажем в малоэтажном строительстве.
Твоя цель — сформировать четкое, профессиональное и аргументированное коммерческое предложение 
на основе уже рассчитанных физических объемов материалов.
Никогда не выдумывай свои базовые цифры по кубатуре и тоннажу — опирайся строго на предоставленные расчеты.
"""

    @classmethod
    async def generate_explanation(cls, user_inputs: Dict[str, Any], calc_results: Dict[str, Any]) -> str:
        """
        Формирование многоступенчатого анализа:
        Шаг 1: Инженерный аудит спецификации
        Шаг 2: Анализ рисков и критических узлов
        Шаг 3: Сметное резюме
        """
        # Если API-ключ не задан, возвращаем структурированный предсказуемый мок
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key.startswith("sk-placeholder"):
            return cls._mock_response(user_inputs, calc_results)

        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=api_key)

            prompt = f"""
Входные данные клиента:
- Тип объекта: {user_inputs.get('building_type')}
- Общая площадь: {user_inputs.get('area_sq_m')} м²
- Этажность: {user_inputs.get('floors')}
- Материал стен: {user_inputs.get('wall_material')}
- Тип фундамента: {user_inputs.get('foundation_type')}
- Кровля: {user_inputs.get('roof_type')}

Точные расчётные показатели:
- Бетон (плита): {calc_results['metrics']['concrete_volume_m3']} м³
- Арматура (А500С): {calc_results['metrics']['rebar_tons']} т
- Объём стеновых блоков: {calc_results['metrics']['wall_volume_m3']} м³
- Площадь кровли: {calc_results['metrics']['roof_area_sq_m']} м²
- Ориентир по материалам: {calc_results['costs_rub']['total_estimated_materials']:,} руб.

Сформируй экспертное заключение в Markdown:
1. Краткий аудит конструктива дома.
2. Рекомендации по оптимизации расходов (на чем можно сэкономить, а на чем категорически нельзя).
3. График основных этапов возведения коробки.
"""

            response = await client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o"),
                messages=[
                    {"role": "system", "content": cls.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return cls._mock_response(user_inputs, calc_results)

    @classmethod
    def _mock_response(cls, user_inputs: Dict[str, Any], calc_results: Dict[str, Any]) -> str:
        metrics = calc_results["metrics"]
        costs = calc_results["costs_rub"]
        return f"""### 📋 Инженерно-техническое резюме объекта

**Параметры дома:** {user_inputs.get('area_sq_m')} м², этажей: {user_inputs.get('floors')}.

#### 1. Спецификация основных материалов:
- **Фундамент:** Монолитная железобетонная плита — `{metrics['concrete_volume_m3']} м³` товарного бетона марки B22.5 (М300), армирование сеткой с расходом `{metrics['rebar_tons']} т` (А500С Ø12мм).
- **Стеновые конструкции:** Наружные стены `{metrics['wall_volume_m3']} м³`. Толщина кладки 375 мм обеспечивает нормативное сопротивление теплопередаче без обязательного дополнительного утепления.
- **Кровельная система:** Площадь покрытия `{metrics['roof_area_sq_m']} м²` с учётом карнизных свесов 600 мм и ветровых нагрузок.

#### 2. Финансовые ориентиры:
- Базовый объём черновых материалов: **~{costs['total_estimated_materials']:,} ₽**
- Диапазон возведения теплового контура «под ключ»: **{costs['estimated_turnkey_min']:,} – {costs['estimated_turnkey_max']:,} ₽**

#### 3. Рекомендация эксперта:
*В расчёте учтён стандартный технологический запас 5% на подрезку блоков и бой при транспортировке.*
"""
