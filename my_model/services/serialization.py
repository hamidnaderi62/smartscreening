import numpy as np


def convert_numpy_to_python(obj):
    """Recursively convert numpy values into JSON-compatible Python values."""
    if obj is None:
        return None
    if isinstance(obj, dict):
        # NumPy scalars can also be used as dictionary keys by calculators.
        # Normalize keys as well as values before Django's JSONField sees them.
        return {
            convert_numpy_to_python(key): convert_numpy_to_python(value)
            for key, value in obj.items()
        }
    if isinstance(obj, (list, tuple)):
        return [convert_numpy_to_python(item) for item in obj]
    if isinstance(obj, np.ndarray):
        return convert_numpy_to_python(obj.tolist())
    if isinstance(obj, np.generic):
        return convert_numpy_to_python(obj.item())
    if isinstance(obj, (set, frozenset)):
        return [convert_numpy_to_python(item) for item in obj]
    if hasattr(obj, 'item') and callable(getattr(obj, 'item')):
        try:
            return convert_numpy_to_python(obj.item())
        except (ValueError, TypeError):
            pass
    return obj
