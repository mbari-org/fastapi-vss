[![MBARI](https://www.mbari.org/wp-content/uploads/2014/11/logo-mbari-3b.png)](http://www.mbari.org)

[![semantic-release](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg)](https://github.com/semantic-release/semantic-release)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/language-Python-blue.svg)](https://www.python.org/downloads/)

**fastapi-vss** is a RESTful API for vector similarity search. It uses the Python web framework FastAPI
 and Redis, the world’s fastest vector database.

This API accelerates machine learning workflows by enabling vector similarity search with ViT (Vision Transformer) 
classification models. It is especially useful for applications such as image retrieval, where you need to find images 
similar to a given query image—for example, in rare event mining, anomaly detection, or other tasks that require 
identifying visually similar images.

We have found it particularly fast and effective for searching large datasets of marine-related images
(e.g., plankton, deepwater animals, or drone imagery) when looking for rare examples or assigning labels to 
unlabeled data, especially when only a limited number of labeled examples are available.

**Author:** [Danelle Cline](https://github.com/danellecline)

---

## Features

- 🔍 Vector similarity search using fast Redis; you can search for similar images based on vector embeddings with a simple API call. Redis is an in-memory data structure store that supports fast vector search.
- 📊 Supports foundational models like DINO and fine-tuned models for specific tasks.
- Support batch processing for efficient querying of multiple images. Default batch size is 32; you can adjust it with the `BATCH_SIZE` environment variable to adjust to the available GPU memory.
- Supports top-n search, where you can specify how many similar predictions to return, e.g. `top_n=5` to return the top 5 similar predictions, where a prediction includes a score and the database id of the closest match.
- Supports returning the database ID, assuming the ID is the stem of the filenames used to generate the vector references. This can be used to retrieve the original image. See the [internal MBARI AI docs](https://docs.mbari.org/internal/ai/) for more details.
- 📦 Docker container for easy deployment
- 📜 OpenAPI documentation for easy integration

---
![](https://raw.githubusercontent.com/mbari-org/fastapi-vss/main/docs/imgs//restwebui.png)

## Related work

* https://github.com/mbari-org/vitstrain
