import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def preload_models():
    # Check if sign_language.pt exists
    model_path = os.path.join(os.path.dirname(__file__), "models", "sign_language.pt")
    if os.path.exists(model_path):
        try:
            import torch
            device = torch.device("cpu")
            torch.load(model_path, map_location=device)
            logger.info("sign_language.pt preloaded successfully.")
        except Exception as e:
            logger.warning(f"sign_language.pt could not be preloaded: {e}")
    else:
        logger.warning("sign_language.pt not found in models/. Backend will start in MODEL_NOT_FOUND mode.")

if __name__ == "__main__":
    logger.info("Starting model preloading...")
    preload_models()
    logger.info("Model preloading complete.")
