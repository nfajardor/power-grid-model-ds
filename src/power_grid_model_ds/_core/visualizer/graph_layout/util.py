from pyproj import Transformer
import numpy as np


_TO_MERC = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
_TO_GEO  = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)

def to_web_mercator(lonlat: np.ndarray) -> np.ndarray:
    """[lon, lat] (EPSG:4326) -> [x, y] en Web Mercator (EPSG:3857)."""
    x, y = _TO_MERC.transform(lonlat[:, 0], lonlat[:, 1])
    return np.column_stack((x, y))

def to_lonlat(merc_xy: np.ndarray) -> np.ndarray:
    """[x, y] en Web Mercator (EPSG:3857) -> [lon, lat] (EPSG:4326)."""
    lon, lat = _TO_GEO.transform(merc_xy[:, 0], merc_xy[:, 1])
    return np.column_stack((lon, lat))