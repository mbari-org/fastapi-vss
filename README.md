[![MBARI](https://www.mbari.org/wp-content/uploads/2014/11/logo-mbari-3b.png)](http://www.mbari.org)
[![Python](https://img.shields.io/badge/language-Python-blue.svg)](https://www.python.org/downloads/)

**fastapi-vss** A RESTful API for vector similarity search.  It uses the Python web framework [FastAPI](https://fastapi.tiangolo.com/)
and the Redis database enabled as Vector database to provide a fast and efficient way to search for similar images 
based on vector embeddings in either real-time or batch mode.

This accelerates machine learning workflows using vector similarity search with classification models.
It is particularly useful for applications like image retrieval, where you want to find images similar to a given query image
for mining rare events, anomaly detection, or other tasks that require finding similar images.

This can be used with a foundational model and does not require a custom trained model, but it is more effective with a fine-tuned model.

---

## Features

- 🔍 Vector similarity search using fast Redis; you can search for similar images based on vector embeddings with a simple API call. Redis is an in-memory data structure store that supports fast vector search.
- 📊 Supports foundational models like DINO and fine-tuned models for specific tasks.
- Support batch processing for efficient querying of multiple images. Default batch size is 32; you can adjust it with the `BATCH_SIZE` environment variable to adjust to the available GPU memory.
- Supports top-n search, where you can specify how many similar predictions to return, e.g. `top_n=5` to return the top 5 similar predictions, where a prediction includes a score and the database id of the closest match.
- The database ID corresponds to the image ID in the Tator database, which can be used to retrieve the original image. See the [MBARI AI docs](https://docs.mbari.org/internal/ai/) for more details.
- 📦 Docker container for easy deployment
- 📜 OpenAPI documentation for easy integration

---
![](https://raw.githubusercontent.com/mbari-org/fastapi-vss/main/docs/imgs//restwebui.png)

## Related work

* https://github.com/mbari-org/aidata
