[![MBARI](https://www.mbari.org/wp-content/uploads/2014/11/logo-mbari-3b.png)](http://www.mbari.org)

[![semantic-release](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg)](https://github.com/semantic-release/semantic-release)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/language-Python-blue.svg)](https://www.python.org/downloads/)

**fastapi-vss** is a RESTful API for vector similarity search. It uses the Python web framework FastAPI
and **Redis**, the fastest vector database available. Redis Stack's in-memory architecture and RediSearch
vector indexes deliver sub-millisecond KNN queries, making it ideal for high-throughput similarity search.

This API accelerates machine learning workflows by enabling vector similarity search with ViT (Vision Transformer) classification models. It is especially useful for applications such as image retrieval, where you need to find images similar to a given query image—for example, in rare event mining, anomaly detection, or other tasks that require identifying visually similar images.

We have found it particularly fast and effective for searching large datasets of marine-related images
(e.g., plankton, deepwater animals, or drone imagery) when looking for rare examples or assigning labels to 
unlabeled data, especially when only a limited number of labeled examples are available. 

**Author:** [Danelle Cline](https://github.com/danellecline)

---

## Architecture Highlights

**Built on Redis.** This design centers on Redis as the vector store and job queue. Redis Stack combines in-memory speed with RediSearch vector search—often the fastest option for vector similarity workloads.

**Optimized for high-throughput batching.** The pipeline is tuned for batch inference: configurable `BATCH_SIZE` (default 32) can be set to maximize GPU capacity; RQ (Redis Queue) decouples the API from inference so requests are enqueued and processed asynchronously; multiple workers run in parallel (one per project); and preprocessing uses a thread pool for parallel image loading. Together, these choices maximize throughput for large image sets.

**Project isolation via separate databases.** Each project has its own configuration and can use a dedicated Redis instance (host/port). The API maintains separate connections and queues per project, and workers are spawned per project, each bound to that project's Redis. This keeps vector indexes and job queues isolated, so data never mixes and projects can be scaled independently.

---

## Features

- 🔍 Vector similarity search using Redis—the fastest vector database available—for sub-millisecond KNN search over embeddings.
- 📊 Supports foundational models like DINO and fine-tuned models for specific tasks.
- Support batch processing for efficient querying of multiple images.  
- Supports top-n search, where you can specify how many similar predictions to return, e.g. `top_n=5` to return the top 5 similar predictions, where a prediction includes a score and the database id of the closest match.
- Supports returning the Tator database UUID or other unique ID where the ID is the stem of the filenames used to generate the vector references. This can be used to retrieve the original image. See the [internal MBARI AI docs](https://docs.mbari.org/internal/ai/) for more details.
- 📦 Docker container for easy deployment
- 📜 OpenAPI documentation for easy integration
- 🔗 URL-based configuration support for remote config management

---
![](https://raw.githubusercontent.com/mbari-org/fastapi-vss/main/docs/imgs//restwebui.png)

## Configuration

The application uses YAML configuration files located in the directory specified by the `CONFIG_PATH` environment variable. Each configuration file defines settings for a project, including Redis connection details and VSS (Vector Similarity Search) model configuration.

### Basic Configuration

A typical configuration file (`config.yml`) looks like this:

```yaml
redis:
  host: "redis"
  port: 6379
  project: "testproject"

vss:
  model: "google/vit-base-patch16-224"  # Hugging Face model ID or local path
  project: "testproject"  # Project name for VSS
  output_path: "/data/vss/outputs"  # Directory where VSS saves JSON results
```

### URL-Based Configuration

You can override or extend your local configuration by fetching settings from a remote URL. This is useful for:
- Centralized configuration management
- Environment-specific settings (dev, staging, production)
- Dynamic configuration updates without redeploying

To use URL-based configuration, add a `config_url` field to your local `config.yml`:

```yaml
config_url: "https://example.com/remote-config.yml"

redis:
  host: "redis"
  port: 6379
  project: "testproject"

vss:
  model: "google/vit-base-patch16-224"
  project: "testproject"
  output_path: "/data/vss/outputs"
```

**How it works:**
1. The application first reads your local `config.yml` file
2. If a `config_url` field is present, it fetches the YAML configuration from that URL
3. The remote configuration is merged with the local configuration using a deep merge
4. **Remote values override local values** for matching keys
5. Local values are preserved for keys that don't exist in the remote config
6. The `config_url` field itself is removed from the final configuration (it's only used for fetching)

**Example merge behavior:**

Local config:
```yaml
config_url: "https://example.com/config.yml"
redis:
  host: "localhost"
  port: 6379
vss:
  model: "local-model"
  project: "myproject"
```

Remote config:
```yaml
redis:
  host: "production-redis.example.com"
vss:
  model: "production-model"
  output_path: "/prod/outputs"
```

Final merged config:
```yaml
redis:
  host: "production-redis.example.com"  # Overridden by remote
  port: 6379  # Preserved from local
vss:
  model: "production-model"  # Overridden by remote
  project: "myproject"  # Preserved from local
  output_path: "/prod/outputs"  # Added from remote
```

**Error handling:**
- If the URL is unreachable or returns an error, the application will fail to start with a clear error message
- If the remote YAML is invalid, the application will fail to start with a parsing error
- The timeout for fetching remote config is 30 seconds

---

## Related work

Models training code
* https://github.com/mbari-org/vitstrain
