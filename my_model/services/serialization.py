import numpy as np


def convert_numpy_to_python(obj):
    """Recursively convert numpy values into JSON-compatible Python values."""
    if obj is None:
        return None
    if isinstance(obj, dict):
        return {key: convert_numpy_to_python(value) for key, value in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [convert_numpy_to_python(item) for item in obj]
    if isinstance(obj, (np.integer, np.int32, np.int64)):
        return int(obj)
    if isinstance(obj, (np.floating, np.float32, np.float64)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.bool_):
        return bool(obj)
    if hasattr(obj, 'item') and callable(getattr(obj, 'item')):
        try:
            return obj.item()
        except (ValueError, TypeError):
            pass
    return obj
