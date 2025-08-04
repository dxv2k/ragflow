"""
Timing utilities for MonkeyOCR model inference performance analysis.

This module provides utilities to collect, analyze, and report timing information
for YOLO layout model and Qwen2.5VL model inference.
"""

import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from loguru import logger
import threading


@dataclass
class ModelTimingData:
    """Data class to store timing information for model inference."""

    model_name: str
    inference_time: float
    num_items: int
    time_per_item: float
    timestamp: float
    additional_info: Optional[Dict[str, Any]] = None


class TimingCollector:
    """
    A thread-safe collector for model inference timing data.

    This class provides methods to collect timing information from different
    model inference stages and generate performance reports.
    """

    def __init__(self):
        """Initialize the timing collector."""
        self._timing_data: List[ModelTimingData] = []
        self._lock = threading.Lock()

    def add_timing(self, model_name: str, inference_time: float, num_items: int, additional_info: Optional[Dict[str, Any]] = None) -> None:
        """
        Add timing data for a model inference.

        Args:
            model_name: Name of the model (e.g., 'YOLO Layout', 'Qwen2.5VL')
            inference_time: Total inference time in seconds
            num_items: Number of items processed
            additional_info: Additional timing information
        """
        time_per_item = inference_time / num_items if num_items > 0 else 0

        timing_data = ModelTimingData(
            model_name=model_name, inference_time=inference_time, num_items=num_items, time_per_item=time_per_item, timestamp=time.time(), additional_info=additional_info or {}
        )

        with self._lock:
            self._timing_data.append(timing_data)

    def get_timing_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of collected timing data.

        Returns:
            Dictionary containing timing summary statistics
        """
        with self._lock:
            if not self._timing_data:
                return {"message": "No timing data collected"}

            # Group by model name
            model_groups = {}
            for data in self._timing_data:
                if data.model_name not in model_groups:
                    model_groups[data.model_name] = []
                model_groups[data.model_name].append(data)

            summary = {}
            for model_name, data_list in model_groups.items():
                total_inference_time = sum(d.inference_time for d in data_list)
                total_items = sum(d.num_items for d in data_list)
                avg_time_per_item = total_inference_time / total_items if total_items > 0 else 0

                summary[model_name] = {
                    "total_inference_time": round(total_inference_time, 3),
                    "total_items_processed": total_items,
                    "average_time_per_item": round(avg_time_per_item, 3),
                    "number_of_batches": len(data_list),
                    "average_batch_time": round(total_inference_time / len(data_list), 3) if data_list else 0,
                }

            return summary

    def log_timing_summary(self) -> None:
        """Log the timing summary to the logger."""
        summary = self.get_timing_summary()

        if "message" in summary:
            logger.info(summary["message"])
            return

        logger.info("=== Model Inference Timing Summary ===")
        for model_name, stats in summary.items():
            logger.info(f"\n{model_name}:")
            logger.info(f"  Total inference time: {stats['total_inference_time']}s")
            logger.info(f"  Total items processed: {stats['total_items_processed']}")
            logger.info(f"  Average time per item: {stats['average_time_per_item']}s")
            logger.info(f"  Number of batches: {stats['number_of_batches']}")
            logger.info(f"  Average batch time: {stats['average_batch_time']}s")
        logger.info("=====================================")

    def export_timing_data(self, filepath: str) -> None:
        """
        Export timing data to a JSON file.

        Args:
            filepath: Path to the output JSON file
        """
        with self._lock:
            data_to_export = [asdict(data) for data in self._timing_data]

        with open(filepath, "w") as f:
            json.dump(data_to_export, f, indent=2)

        logger.info(f"Timing data exported to {filepath}")

    def clear_timing_data(self) -> None:
        """Clear all collected timing data."""
        with self._lock:
            self._timing_data.clear()
        logger.info("Timing data cleared")


# Global timing collector instance
_timing_collector = TimingCollector()


def get_timing_collector() -> TimingCollector:
    """
    Get the global timing collector instance.

    Returns:
        Global TimingCollector instance
    """
    return _timing_collector


class TimingContext:
    """
    Context manager for timing model inference operations.

    This class provides a convenient way to time operations and automatically
    add the timing data to the global collector.
    """

    def __init__(self, model_name: str, num_items: int, additional_info: Optional[Dict[str, Any]] = None):
        """
        Initialize the timing context.

        Args:
            model_name: Name of the model being timed
            num_items: Number of items being processed
            additional_info: Additional information to store with timing data
        """
        self.model_name = model_name
        self.num_items = num_items
        self.additional_info = additional_info or {}
        self.start_time = None

    def __enter__(self):
        """Start timing when entering the context."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing and record data when exiting the context."""
        if self.start_time is not None:
            inference_time = time.time() - self.start_time
            get_timing_collector().add_timing(self.model_name, inference_time, self.num_items, self.additional_info)


def time_model_inference(model_name: str, num_items: int, additional_info: Optional[Dict[str, Any]] = None):
    """
    Decorator to time model inference functions.

    Args:
        model_name: Name of the model being timed
        num_items: Number of items being processed
        additional_info: Additional information to store with timing data

    Returns:
        Decorator function
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            with TimingContext(model_name, num_items, additional_info):
                return func(*args, **kwargs)

        return wrapper

    return decorator
