import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def preload_yolo():
    try:
        from ultralytics import YOLO
        logger.info("Preloading YOLOv8n model...")
        YOLO("yolov8n.pt")
        logger.info("YOLO model preloaded successfully.")
    except ImportError:
        logger.warning("Ultralytics not installed. Skipping YOLO preload.")
    except Exception as e:
        logger.error(f"Error preloading YOLO: {e}")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("Starting model preloading...")
    preload_yolo()
    logger.info("Model preloading complete.")
