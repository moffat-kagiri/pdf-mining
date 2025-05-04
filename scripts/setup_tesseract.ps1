import torch
from yolov5 import train

def train_yolo_model(data_yaml: str, epochs: int = 50):
    train.run(
        data=data_yaml,
        epochs=epochs,
        weights="yolov5s.pt",
        imgsz=640
    )