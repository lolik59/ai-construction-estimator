from typing import Dict, Any

class ConstructionCalculator:
    """
    Детерминированный калькулятор строительных объемов.
    Исключает арифметические ошибки и галлюцинации LLM.
    """

    PRICES = {
        "concrete_per_m3": 5800,       # Бетон М300 с доставкой
        "rebar_per_ton": 62000,        # Арматура А500С
        "aerated_block_per_m3": 6900,  # Газобетон D500
        "brick_per_m3": 8500,          # Кирпич облицовочный
        "metal_roof_per_m2": 1800,     # Металлочерепица с крепежом
        "soft_roof_per_m2": 2400,      # Мягкая кровля
    }

    @classmethod
    def calculate(cls, area_sq_m: float, floors: int, wall_material: str, foundation_type: str, roof_type: str) -> Dict[str, Any]:
        footprint_area = area_sq_m / max(floors, 1)

        # 1. Расчёт фундамента (плита толщиной 30см или лента)
        if foundation_type == "monolithic_slab":
            concrete_volume = footprint_area * 0.30 * 1.05  # +5% технологический запас
            rebar_tons = concrete_volume * 0.08             # ~80 кг на 1 м3 бетона
        else:
            concrete_volume = (footprint_area ** 0.5 * 4) * 0.4 * 1.5 * 1.05
            rebar_tons = concrete_volume * 0.06

        # 2. Расчёт стен (периметр * высота этажа 3м * количество этажей за вычетом 20% на проёмы)
        perimeter = (footprint_area ** 0.5) * 4
        wall_height = floors * 3.0
        wall_area = perimeter * wall_height * 0.80  # вычет окон и дверей
        wall_volume = wall_area * 0.375             # толщина блока 375мм

        # 3. Расчёт кровли (площадь пятна застройки + свесы 1.25 коэфф. уклона)
        roof_area = footprint_area * 1.25

        # 4. Расчёт базовой стоимости материалов
        concrete_cost = concrete_volume * cls.PRICES["concrete_per_m3"]
        rebar_cost = rebar_tons * cls.PRICES["rebar_per_ton"]
        
        block_unit_price = cls.PRICES["aerated_block_per_m3"] if wall_material == "aerated_concrete" else cls.PRICES["brick_per_m3"]
        wall_cost = wall_volume * block_unit_price

        roof_unit_price = cls.PRICES["metal_roof_per_m2"] if roof_type == "metal_tile" else cls.PRICES["soft_roof_per_m2"]
        roof_cost = roof_area * roof_unit_price

        total_material_cost = concrete_cost + rebar_cost + wall_cost + roof_cost

        return {
            "metrics": {
                "footprint_area_sq_m": round(footprint_area, 1),
                "concrete_volume_m3": round(concrete_volume, 2),
                "rebar_tons": round(rebar_tons, 2),
                "wall_volume_m3": round(wall_volume, 2),
                "roof_area_sq_m": round(roof_area, 1),
            },
            "costs_rub": {
                "foundation_cost": int(concrete_cost + rebar_cost),
                "wall_material_cost": int(wall_cost),
                "roof_material_cost": int(roof_cost),
                "total_estimated_materials": int(total_material_cost),
                "estimated_turnkey_min": int(total_material_cost * 2.2), # Работа + механизация + черновая отделка
                "estimated_turnkey_max": int(total_material_cost * 2.8)
            }
        }
