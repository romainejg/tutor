"""Curriculum catalog for CEA scenario practice."""

from __future__ import annotations

from typing import Dict, List


class CurriculumManager:
    """Provides role/module/concept curriculum lookups."""

    def __init__(self) -> None:
        self._curriculum: Dict[str, Dict[str, Dict[str, List[str] | str]]] = {
            "Plant Scientist": {
                "description": "Diagnoses crop physiology and nutrient transport issues.",
                "modules": {
                    "Tipburn and calcium transport": [
                        "calcium mobility",
                        "transpiration",
                        "VPD",
                        "rapid growth",
                        "inner leaf development",
                    ],
                    "Mineral nutrition": [
                        "nitrogen form",
                        "potassium",
                        "calcium",
                        "magnesium",
                        "micronutrients",
                        "nutrient antagonism",
                    ],
                    "Light response": [
                        "DLI",
                        "PPFD",
                        "photoperiod",
                        "spectrum",
                        "photosynthesis",
                        "morphology",
                    ],
                    "Root-zone health": [
                        "dissolved oxygen",
                        "root pathogens",
                        "temperature",
                        "biofilm",
                        "root browning",
                    ],
                    "Stress physiology": [
                        "heat stress",
                        "low oxygen stress",
                        "water stress",
                        "oxidative stress",
                    ],
                },
            },
            "Product Developer": {
                "description": "Optimizes post-harvest quality and product consistency.",
                "modules": {
                    "Shelf life": [
                        "senescence",
                        "water loss",
                        "respiration rate",
                        "harvest maturity",
                        "packaging effects",
                    ],
                    "Flavor and texture": [
                        "bitterness",
                        "crunch",
                        "dry matter",
                        "secondary metabolites",
                        "cultivar selection",
                    ],
                    "Trial design": [
                        "controls",
                        "replication",
                        "randomization",
                        "measurable endpoints",
                        "statistical thinking",
                    ],
                    "Cultivar screening": [
                        "genotype by environment interaction",
                        "yield stability",
                        "quality traits",
                        "disease tolerance",
                    ],
                    "Product quality": [
                        "color",
                        "texture",
                        "nutrition",
                        "consistency",
                        "defect thresholds",
                    ],
                },
            },
            "Grower": {
                "description": "Balances climate and operations to maximize yield and quality.",
                "modules": {
                    "Climate control": [
                        "temperature",
                        "VPD",
                        "humidity",
                        "airflow",
                        "CO2",
                        "light interaction",
                    ],
                    "Irrigation and fertigation": [
                        "EC",
                        "pH",
                        "irrigation frequency",
                        "leaching",
                        "nutrient balance",
                    ],
                    "Crop scheduling": [
                        "transplant timing",
                        "spacing",
                        "growth rate",
                        "harvest windows",
                        "uniformity",
                    ],
                    "Root-zone management": [
                        "oxygen",
                        "water temperature",
                        "sanitation",
                        "Pythium risk",
                        "nutrient delivery",
                    ],
                    "Yield-quality optimization": [
                        "density",
                        "DLI",
                        "harvest age",
                        "tipburn risk",
                        "labor timing",
                    ],
                },
            },
        }

    def get_roles(self) -> List[str]:
        return list(self._curriculum.keys())

    def get_modules_by_role(self, role_name: str) -> List[str]:
        role_data = self._curriculum.get(role_name, {})
        return list(role_data.get("modules", {}).keys())

    def get_concepts_by_module(self, role_name: str, module_name: str) -> List[str]:
        role_data = self._curriculum.get(role_name, {})
        modules = role_data.get("modules", {})
        return list(modules.get(module_name, []))

    def get_all_curriculum(self) -> Dict[str, Dict[str, Dict[str, List[str] | str]]]:
        return self._curriculum
