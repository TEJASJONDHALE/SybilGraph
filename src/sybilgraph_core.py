"""Compatibility facade for the SybilGraph backend."""

from .data_generation import COUPON_CATALOG, generate_synthetic_data
from .detector import RingDetector
from .evaluation import calibrate_thresholds, evaluate_pipeline

__all__ = [
    "COUPON_CATALOG",
    "generate_synthetic_data",
    "RingDetector",
    "calibrate_thresholds",
    "evaluate_pipeline",
]
