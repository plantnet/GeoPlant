"""GeoPlant dataset downloader package."""

__all__ = ["GeoPlant"]


def __getattr__(name: str):
    """Lazily expose public package attributes."""
    if name == "GeoPlant":
        from .geoplant import GeoPlant

        return GeoPlant
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
