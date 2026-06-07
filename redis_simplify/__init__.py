"""redis-simplify - Wrapper de conveniência para Redis"""
from .client import RedisClient

def _get_version():
    try:
        from importlib.metadata import version
        return version("redis-simplify")
    except Exception:
        try:
            import tomllib
            from pathlib import Path
            pyproject = Path(__file__).parent.parent / "pyproject.toml"
            if pyproject.exists():
                data = tomllib.loads(pyproject.read_text())
                return data["project"]["version"]
        except Exception:
            pass
        return "0.1.0"

__version__ = _get_version()
__all__ = ["RedisClient"]