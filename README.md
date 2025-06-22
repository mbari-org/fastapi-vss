[![MBARI](https://www.mbari.org/wp-content/uploads/2014/11/logo-mbari-3b.png)](http://www.mbari.org)
[![Python](https://img.shields.io/badge/language-Python-blue.svg)](https://www.python.org/downloads/)

**fastapi-vss** A RESTful API for vector similarity search.  It uses the Python web framework [FastAPI](https://fastapi.tiangolo.com/).

This accelerates machine learning workflows using vector similarity search with classification models.
This does not require a custom trained model, but it is more effective with a fine-tuned model.

---

## Features

- 🔍 Vector similarity search using fast Redis; you can search for similar images based on vector embeddings with a simple API call. Redis is an in-memory data structure store that supports fast vector search.
- 📊 Supports foundational models like CLIP, and fine-tuned models for specific tasks.
- Support batch processing for efficient querying of multiple images. Default batch size is 32; you can adjust it with the `BATCH_SIZE` environment variable.
- Supports top-n search, where you can specify how many similar predictions to return, e.g. `top_n=5` to return the top 5 similar predictions, where a prediction includes a score and the database id of the closest match.
- 📦 Docker container for easy deployment
- 📜 OpenAPI documentation for easy integration

---
![](https://raw.githubusercontent.com/mbari-org/fastapi-vss/main/docs/imgs//restwebui.png)

## Related work

* https://github.com/mbari-org/aidata
