[![MBARI](https://www.mbari.org/wp-content/uploads/2014/11/logo-mbari-3b.png)](http://www.mbari.org)
[![Python](https://img.shields.io/badge/language-Python-blue.svg)](https://www.python.org/downloads/)

**fastapi-vss** A RESTful API for vector similarity search.  It uses the Python web framework [FastAPI](https://fastapi.tiangolo.com/). 

This accelerates machine learning workflows that require vector similarity search using classification models.

--- 
![](https://raw.githubusercontent.com/mbari-org/fastapi-vss/main/docs/imgs//restwebui.png)
---

## Features

- 🔍 Vector similarity search using Redis; you can search for similar images based on vector embeddings with a simple API call.
- 📊 Supports foundational models like CLIP, and fine-tuned models for specific tasks.
- Support batch processing for efficient querying of multiple images. Default batch size is 32; you can adjust it with the `BATCH_SIZE` environment variable.
- 📦 Docker container for easy deployment
- 📜 OpenAPI documentation for easy integration

## Installation

```bash
pip install fastapi-vss
```

## Related work
 
* https://github.com/mbari-org/aidata
