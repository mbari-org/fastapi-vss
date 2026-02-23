import sys
import time

import requests

BASE_URL = "http://localhost:8000"
PROJECT = "testproject"
IMAGE_PATH = "tests/images/mammal/elephant.jpg"
POLL_INTERVAL = 2
MAX_WAIT = 60
EXPECTED_EMBEDDING_DIM = 768


def test_embed_endpoint():
    with open(IMAGE_PATH, "rb") as f:
        files = [("files", ("elephant.jpg", f, "image/jpeg"))]
        response = requests.post(f"{BASE_URL}/embed/{PROJECT}", files=files)

    assert response.status_code == 200, f"POST /embed failed: {response.status_code} {response.text}"
    data = response.json()
    assert "job_id" in data, f"Missing job_id in response: {data}"
    job_id = data["job_id"]
    print(f"Submitted embedding job: {job_id}")

    elapsed = 0
    result = None
    while elapsed < MAX_WAIT:
        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL
        poll = requests.get(f"{BASE_URL}/predict/job/{job_id}/{PROJECT}")
        poll_data = poll.json()
        print(f"  [{elapsed}s] Job status: {poll_data.get('status', 'unknown')}")

        if poll_data.get("status") == "done":
            result = poll_data["result"]
            break
        if poll_data.get("status") == "failed":
            print(f"FAIL: Job failed: {poll_data}")
            sys.exit(1)

    assert result is not None, f"Job did not complete within {MAX_WAIT}s"

    assert "filenames" in result, f"Missing 'filenames' in result: {result.keys()}"
    assert "embeddings" in result, f"Missing 'embeddings' in result: {result.keys()}"

    assert result["filenames"] == ["elephant.jpg"], (
        f"Expected filenames ['elephant.jpg'], got {result['filenames']}"
    )

    embeddings = result["embeddings"]
    assert len(embeddings) == 1, f"Expected 1 embedding, got {len(embeddings)}"
    assert len(embeddings[0]) == EXPECTED_EMBEDDING_DIM, (
        f"Expected embedding dimension {EXPECTED_EMBEDDING_DIM}, got {len(embeddings[0])}"
    )

    assert all(isinstance(v, float) for v in embeddings[0]), "Embedding values should be floats"

    print(f"PASS: Got embedding of dimension {len(embeddings[0])} for elephant.jpg")
    print(f"  First 5 values: {embeddings[0][:5]}")
    print(f"  Last 5 values:  {embeddings[0][-5:]}")


if __name__ == "__main__":
    test_embed_endpoint()