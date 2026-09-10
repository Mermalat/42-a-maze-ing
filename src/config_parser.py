from pathlib import Path
from dataclasses import dataclass


@dataclass
class Config:
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool


class ConfigError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

    def __str__(self) -> str:
        return "Invalid configuration file"


def parse_config(file_path: str) -> Config:
    path = Path(file_path)

    if not path.exists():
        raise ConfigError("Configuration file not found")

    data: dict[str, str] = {}

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("=")
            if len(parts) != 2:
                raise ConfigError(f"Invalid configuration line: {line}")

            key = parts[0].strip()
            value = parts[1].strip()
            data[key] = value

    required_keys = {
        "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"
        }
    missing = required_keys - set(data.keys())
    if missing:
        raise ConfigError(f"Missing required configuration keys: {missing}")

    try:
        width = int(data["WIDTH"])
        height = int(data["HEIGHT"])
        if width <= 0 or height <= 0:
            raise ConfigError("Width and height must be positive integers")
        entry = tuple(map(int, data["ENTRY"].split(",")))
        exit = tuple(map(int, data["EXIT"].split(",")))
        if not (0 <= entry[0] < width and 0 <= entry[1] < height):
            raise ConfigError("Entry point is out of bounds")
        if not (0 <= exit[0] < width and 0 <= exit[1] < height):
            raise ConfigError("Exit point is out of bounds")
        if (entry[0], entry[1]) == (exit[0], exit[1]):
            raise ConfigError("Entry and exit points cannot be the same")
        output_file = data["OUTPUT_FILE"]
        perfect = data["PERFECT"].lower() in ("true", "1", "yes")

        return Config(
            width=width,
            height=height,
            entry=(entry[0], entry[1]),
            exit=(exit[0], exit[1]),
            output_file=output_file,
            perfect=perfect,
        )
    except ValueError as e:
        raise ConfigError(f"Configuration error: {e}")
