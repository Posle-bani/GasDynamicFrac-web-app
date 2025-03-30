from my_app_api.models.models import ReportCalculated, WellState

def calculate_from_well_state(well_state: WellState) -> ReportCalculated:
    """
    Выполняет расчёты на основе состояния скважины и возвращает объект ReportCalculated.
    """
    depth = well_state.depth or 0.0
    pressure = well_state.pressure or 0.0

    # Примерные расчёты — можно заменить формулами из твоей логики
    required_charges = int((depth * pressure) / 1000) if pressure > 0 else 0
    effective_pressure = pressure * 0.9
    gas_volume = depth * 0.5
    impact_duration = pressure / 2 if pressure > 0 else 0

    return ReportCalculated(
        effective_pressure=effective_pressure,
        required_charges=required_charges,
        gas_volume=gas_volume,
        impact_duration=impact_duration
    )
