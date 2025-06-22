import os
from pathlib import Path

import numpy as np
import redis
import torch

from app.predictors.process_vits import ViTWrapper
from app.predictors.vector_similarity import VectorSimilarity

# Load secrets from .env
from dotenv import load_dotenv
load_dotenv()

test_images = Path(__file__).parent / "images" / "atolla"
DEFAULT_MODEL = "google/vit-base-patch16-224"
vector_dimensions = 768  # Default for ViT base model
reset = False
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
r = redis.Redis(host='localhost', port=6379, db=0, password=os.getenv("REDIS_PASSWD"))
vs = VectorSimilarity(r, vector_dimensions=vector_dimensions, reset=reset)
v = ViTWrapper(r,device,DEFAULT_MODEL)

for image_path in test_images.glob("*.jpg"):
    image_path = str(image_path)
    print(f"Processing image: {image_path}")
    inputs = v.preprocess_images([image_path])
    emb = v.get_image_embeddings(inputs)
    emb = emb.astype(np.float32)
    print(f"Loaded embedding for {image_path}: {emb.shape} to redis")
    vs.add_vector(doc_id=f"{image_path.stem}:9999", vector=emb.tobytes(), tag=DEFAULT_MODEL)