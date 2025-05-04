# This module uses LayoutParser to identify layout elements in a document image.
import numpy as np
from typing import List, Any, Optional
import logging
import cv2
import os
from PIL import Image  # Use Pillow instead of PIL

logger = logging.getLogger(__name__)

try:
    import torch
    import layoutparser as lp
    LAYOUT_PARSER_AVAILABLE = True
    logger.info(f"Using PyTorch version: {torch.__version__}")
except ImportError as e:
    logger.warning(f"LayoutParser import failed: {e}")
    LAYOUT_PARSER_AVAILABLE = False

def detect_layout_elements(images, config):
    try:
        model = lp.Detectron2LayoutModel(
            config_path="detectron2_configs/layout.yaml",
            label_map={0: "Text", 1: "Title", 2: "Table", 3: "Figure"}
        )
        layout_elements = []
        for image in images:
            layout = model.detect(image)
            layout_elements.append(layout)
        return layout_elements
    except ImportError as e:
        logging.error(f"Layout detection failed: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Layout detection error: {str(e)}")
        return []