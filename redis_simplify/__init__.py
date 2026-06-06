import tomllib
from pathlib import Path

def _get_version():
    try:
        from importlib.metadata import version
        return version("redis-simplify")
    except Exception:
        # Fallback: lê do pyproject.toml
        try:
            pyproject = Path(__file__).parent.parent / "pyproject.toml"
            if pyproject.exists():
                data = tomllib.loads(pyproject.read_text())
                return data["project"]["version"]
        except Exception:
            pass
        return "0.1.0"  # último recurso

__version__ = _get_version()