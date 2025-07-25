# fastapi-vss, Apache-2.0 license
# Filename: predictors/process_vits.py
# Description: Process images with Vision Transformer (ViT) model and search by KNN embeddings in Redis vector store

import numpy as np
import redis
import torch
from PIL import Image
from transformers import AutoModel, AutoImageProcessor  # type: ignore
from typing import List

from app.predictors.vector_similarity import VectorSimilarity

import logging

logging.basicConfig(level=logging.DEBUG)
debug = logging.debug
info = logging.info
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(console)


class ViTWrapper:
    DEFAULT_MODEL_NAME = "google/vit-base-patch16-224"

    def __init__(self, r: redis.Redis, device, model_name: str = DEFAULT_MODEL_NAME, reset: bool = False, batch_size: int = 32):
        self.r = r
        self.device = device
        self.batch_size = batch_size
        self.processor = AutoImageProcessor.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.vs = VectorSimilarity(r, vector_dimensions=self.vector_dimensions, reset=reset)

    @property
    def vector_dimensions(self) -> int:
        return self.model.config.hidden_size

    def preprocess_images(self, image_paths: List[str]):
        debug(f"Preprocessing {len(image_paths)} images")
        images = [Image.open(image_path).convert("RGB") for image_path in image_paths]
        inputs = self.processor(images=images, return_tensors="pt").to(self.device)
        debug(f"Done preprocessing {len(image_paths)} images, batch size is {inputs['pixel_values'].shape[0]}")
        return inputs

    def get_image_embeddings(self, inputs: torch.Tensor):
        """get embeddings for a batch of images"""
        debug(f"Getting embeddings for batch of size {inputs['pixel_values'].shape[0]}")
        debug(inputs["pixel_values"].shape)  # Should be (B, 3, H, W)

        with torch.no_grad():
            embeddings = self.model(**inputs)
        info("Done getting embeddings for batch")
        batch_embeddings = embeddings.last_hidden_state[:, 0, :].cpu().numpy()
        info(f"Batch embeddings shape: {batch_embeddings.shape}")
        return np.array(batch_embeddings)

    def predict(self, image_paths: List[str], top_n: int = 1) -> tuple[list[list[str]], list[list[float]], list[list[str]]]:
        """Search using KNN for embeddings for a batch of images"""
        predictions = []
        scores = []
        ids = []

        info(f"Found {len(image_paths)} images to predict")
        for i in range(0, len(image_paths), self.batch_size):
            batch = image_paths[i : i + self.batch_size]
            images = self.preprocess_images(batch)
            embeddings = self.get_image_embeddings(images)
            info(f"Searching for {len(embeddings)} embeddings in Redis")
            for j, emb in enumerate(embeddings):
                r = self.vs.search_vector(emb.tobytes(), top_n=top_n)
                # Data is doc:label:id - split it into parts
                data = [x["id"].split(":") for x in r]
                batch_pred = []
                batch_ids = []
                for d in data:
                    batch_pred.append(d[1])
                    batch_ids.append(d[2])

                predictions.append([b for b in batch_pred])
                ids.append([i for i in batch_ids])
                # Separate out the scores for each prediction - this is used later for voting
                scores.append([round(float(x["score"]), 4) for x in r])

        return predictions, scores, ids
