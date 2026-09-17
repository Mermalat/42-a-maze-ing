"""Parser for the project's KEY=VALUE configuration format."""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path


@dataclass(frozen=True)
class Config:
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None
    algorithm: str = "dfs"
    delay: float = 0.02


class ConfigError(Exception):
    """Raised when a configuration file is missing or malformed."""


def parse_config(file_path: str) -> Config:
    """Read and validate a maze configuration file."""
    path = Path(file_path)
    data: dict[str, str] = {}

    try:
        with path.open("r", encoding="utf-8") as stream:
            for line_number, raw_line in enumerate(stream, start=1):
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise ConfigError(
                        f"line {line_number}: expected KEY=VALUE"
                    )
                key, value = (part.strip() for part in line.split("=", 1))
                if not key or not value:
                    raise ConfigError(
                        f"line {line_number}: key and value cannot be empty"
                    )
                if key in data:
                    raise ConfigError(
                        f"line {line_number}: duplicate key {key}"
                    )
                data[key] = value
    except FileNotFoundError as error:
        raise ConfigError(f"configuration file not found: {path}") from error
    except PermissionError as error:
        raise ConfigError(f"permission denied reading: {path}") from error
    except UnicodeError as error:
        raise ConfigError(
            f"configuration is not valid UTF-8: {path}"
        ) from error
    except OSError as error:
        raise ConfigError(f"cannot read {path}: {error}") from error

    required_keys = {
        "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"
        }
    missing = required_keys - data.keys()
    if missing:
        names = ", ".join(sorted(missing))
        raise ConfigError(f"missing required key(s): {names}")

    try:
        width = int(data["WIDTH"])
        height = int(data["HEIGHT"])
        if width <= 0 or height <= 0:
            raise ConfigError("WIDTH and HEIGHT must be positive integers")
        entry = _parse_coordinate(data["ENTRY"], "ENTRY")
        exit_cell = _parse_coordinate(data["EXIT"], "EXIT")
        if not (0 <= entry[0] < width and 0 <= entry[1] < height):
            raise ConfigError("ENTRY is outside the maze")
        if not (
            0 <= exit_cell[0] < width and 0 <= exit_cell[1] < height
        ):
            raise ConfigError("EXIT is outside the maze")
        if entry == exit_cell:
            raise ConfigError("ENTRY and EXIT must be different")
        output_file = data["OUTPUT_FILE"]
        perfect_text = data["PERFECT"].lower()
        if perfect_text not in {"true", "false"}:
            raise ConfigError("PERFECT must be True or False")
        perfect = perfect_text == "true"
        seed = int(data["SEED"]) if "SEED" in data else None
        algorithm = data.get("ALGORITHM", "DFS").lower()
        if algorithm not in {"dfs", "prim"}:
            raise ConfigError("ALGORITHM must be DFS or PRIM")
        try:
            delay = float(data.get("DELAY", "0.02"))
        except ValueError as error:
            raise ConfigError("DELAY must be a number") from error
        if not math.isfinite(delay) or delay < 0:
            raise ConfigError("DELAY must be a finite non-negative number")

        return Config(
            width=width,
            height=height,
            entry=(entry[0], entry[1]),
            exit=exit_cell,
            output_file=output_file,
            perfect=perfect,
            seed=seed,
            algorithm=algorithm,
            delay=delay,
        )
    except ValueError as error:
        raise ConfigError(
            "numeric values must contain valid integers"
        ) from error


def _parse_coordinate(value: str, key: str) -> tuple[int, int]:
    """Parse an exact x,y coordinate pair."""
    parts = value.split(",")
    if len(parts) != 2:
        raise ConfigError(f"{key} must use the x,y format")
    try:
        return int(parts[0].strip()), int(parts[1].strip())
    except ValueError as error:
        raise ConfigError(f"{key} coordinates must be integers") from error
