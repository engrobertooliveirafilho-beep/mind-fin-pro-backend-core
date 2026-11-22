"""Read-only gate for recovered Trader1 exporter configuration.
Original Drive: TRADER_1_007_R5_R2_CANONICAL_EXPORTER.mq5 (1ZZBtTn2r4jj4CHnTgGcnBfkT-rslJ2zL).
No MT5 connection or orders.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class ExporterConfig:
    window_days: int
    minimum_bars: int
    maximum_bars: int

def validate_exporter_config(config: ExporterConfig) -> ExporterConfig:
    if not isinstance(config, ExporterConfig):
        raise ValueError("invalid exporter config")
    for key in ("window_days", "minimum_bars", "maximum_bars"):
        value = getattr(config, key)
        if type(value) is not int:
            raise ValueError(f"{key} must be an integer")
    if config.window_days < 1 or config.window_days > 365:
        raise ValueError("window_days must be between 1 and 365")
    if config.minimum_bars < 1:
        raise ValueError("minimum_bars must be positive")
    if config.maximum_bars < 0:
        raise ValueError("maximum_bars cannot be negative")
    if config.maximum_bars and config.maximum_bars < config.minimum_bars:
        raise ValueError("maximum_bars cannot satisfy minimum_bars")
    return config
