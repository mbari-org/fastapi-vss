# fastapi-vss, Apache-2.0 license
# Filename: predictors/process_vits.py
# Description: Process images with Vision Transformer (ViT) model and search by KNN embeddings in Redis vector store
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import redis
import torch
from PIL import Image
from transformers import AutoModel, AutoImageProcessor  # type: ignore
from typing import List, Any

from app.predictors.vector_similarity import VectorSimilarity

import logging

logging.basicConfig(level=logging.DEBUG)
debug = logging.debug
info = logging.info
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(console)

try:
    import albumentations as A  # type: ignore
    from albumentations.pytorch import ToTensorV2  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    A = None
    ToTensorV2 = None


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

    def _open_rgb(self, image_ref: Any) -> Image.Image:
        # `image_ref` can be a path-like or a file-like object (UploadFile.file).
        if isinstance(image_ref, Image.Image):
            return image_ref.convert("RGB")
        return Image.open(image_ref).convert("RGB")

    def _get_albumentations_transform(self):
        if A is None or ToTensorV2 is None:
            raise RuntimeError("augmentation=albumentations requested, but albumentations is not installed")
        image_size = self._get_processor_image_size()
        return A.Compose(
            [
                A.RandomResizedCrop(size=(image_size, image_size), scale=(0.5, 1.0), p=1.0),
                A.GaussianBlur(blur_limit=(3, 7), sigma_limit=0.1, p=0.5),
                ToTensorV2(),
            ]
        )

    def _get_processor_image_size(self) -> int:
        size = getattr(self.processor, "size", None)
        if isinstance(size, dict):
            if "height" in size:
                return int(size["height"])
            if "width" in size:
                return int(size["width"])
            if "shortest_edge" in size:
                return int(size["shortest_edge"])
        return 224

    def _normalize_pixel_values(self, pixel_values: torch.Tensor) -> torch.Tensor:
        # ViT expects normalized pixel values. Mirror HF AutoImageProcessor mean/std.
        mean = getattr(self.processor, "image_mean", [0.5, 0.5, 0.5])
        std = getattr(self.processor, "image_std", [0.5, 0.5, 0.5])
        mean_t = torch.tensor(mean, dtype=pixel_values.dtype, device=pixel_values.device).view(1, 3, 1, 1)
        std_t = torch.tensor(std, dtype=pixel_values.dtype, device=pixel_values.device).view(1, 3, 1, 1)
        return (pixel_values - mean_t) / std_t

    def preprocess_images(self, image_paths: List[Any]):
        debug(f"Preprocessing {len(image_paths)} images")
        with ThreadPoolExecutor(max_workers=8) as executor:
            images = list(executor.map(self._open_rgb, image_paths))
        inputs = self.processor(images=images, return_tensors="pt", device="cuda")
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

    def predict(
        self,
        image_paths: List[Any],
        top_n: int = 1,
        augmentation: str = "none",
    ) -> tuple[list[list[str]], list[list[float]], list[list[str]]]:
        """Search using KNN for embeddings for a batch of images"""
        predictions = []
        scores = []
        ids = []

        info(f"Found {len(image_paths)} images to predict")
        for i in range(0, len(image_paths), self.batch_size):
            batch = image_paths[i : i + self.batch_size]
            if augmentation == "albumentations":
                transform = self._get_albumentations_transform()
                with ThreadPoolExecutor(max_workers=8) as executor:
                    base_images = list(executor.map(self._open_rgb, batch))

                tensors: list[torch.Tensor] = []
                for img in base_images:
                    out = transform(image=np.array(img))
                    tensors.append(out["image"])

                pixel_values = torch.stack(tensors, dim=0).float()
                pixel_values = self._normalize_pixel_values(pixel_values)
                inputs = {"pixel_values": pixel_values.to(self.device)}
                embeddings = self.get_image_embeddings(inputs)
            else:
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
