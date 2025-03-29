
def calculate_from_well_state(well_state: dict) -> dict:
    """
    Выполняет расчёты на основе данных состояния скважины.
    Примерные формулы — будут уточняться.
    """
    depth = well_state.get("depth", 0)
    pressure = well_state.get("pressure", 0)

    return {
        "effective_pressure": pressure - 1.5 if pressure else None,
        "required_charges": int(depth / 10) if depth else None,
        "gas_volume": round((depth * pressure) / 1000, 2) if depth and pressure else None,
        "impact_duration": 3.5  # заглушка
    }