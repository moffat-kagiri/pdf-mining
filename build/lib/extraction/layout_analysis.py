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

def detect_layout_elements(image: np.ndarray) -> List[Any]:
    """Identify headings, paragraphs, tables using LayoutParser."""
    if not LAYOUT_PARSER_AVAILABLE:
        logger.error("LayoutParser not available")
        return []

    try:
        # Convert numpy array to PIL Image if needed
        if isinstance(image, np.ndarray):
            pil_image = Image.fromarray(image)
        else:
            pil_image = image
        image = np.array(pil_image)

        # Initialize with pre-trained PubLayNet model for CPU
        model = lp.Detectron2LayoutModel(
            config_path="lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config",
            label_map={
                0: "Text",
                1: "Title", 
                2: "List",
                3: "Table",
                4: "Figure"
            },
            extra_config=["MODEL.DEVICE", "cpu"]
        )
        
        layout = model.detect(image)
        return sorted(layout, key=lambda x: x.coordinates[1])
        
    except Exception as e:
        logger.error(f"Layout detection failed: {str(e)}")
        return []