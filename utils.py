# utils.py
def validate_inputs(inputs):
    # Placeholder for input validation
    for key, value in inputs.items():
        if key == "emission_rate" and (value < 0 or value > 100):
            return False
        if key == "intensity" and (value < 0.5 or value > 2.0):
            return False
        if key == "efficiency" and (value < 0 or value > 1):
            return False
        if key == "radius" and (value < 1 or value > 20):
            return False
        if key == "cost" and (value < 1000 or value > 100000):
            return False
        if key == "capacity" and (value < 10 or value > 100):
            return False
    return True
