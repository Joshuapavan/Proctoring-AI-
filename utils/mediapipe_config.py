import os
from utils.logger import logger

def configure_mediapipe():
    """Configure MediaPipe to use CPU"""
    try:
        # Force CPU usage
        os.environ["MEDIAPIPE_CPU_ONLY"] = "1"  # Changed from MEDIAPIPE_GPU_SOLUTION
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
        
        # Additional MediaPipe configurations
        os.environ["MEDIAPIPE_CPU_THREADS"] = "2"  # Reduced thread count
        
        logger.info("MediaPipe configured for CPU-only mode")
    except Exception as e:
        logger.error(f"Failed to configure MediaPipe: {str(e)}")
