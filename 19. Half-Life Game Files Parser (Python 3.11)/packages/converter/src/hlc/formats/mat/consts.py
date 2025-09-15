from .types import MatType



MAT_CODE_TO_TYPE = {
    'C': MatType.Concrete,
    'M': MatType.Metal,
    'Y': MatType.Glass,
    'D': MatType.Dirt,
    'S': MatType.Slosh,
    'T': MatType.Tile,
    'G': MatType.Grate,
    'W': MatType.Wood,
    'F': MatType.Flesh,
    'V': MatType.Vent,
    'P': MatType.Computer
}



__all__ = [
    'MAT_CODE_TO_TYPE',
]