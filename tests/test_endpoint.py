import requests
import time
from pathlib import Path

# Get the directory where this test file is located
TEST_DIR = Path(__file__).parent
IMAGE_PATH = TEST_DIR / "images" / "jelly" / "7e28463e-bab3-5279-b5ea-a741c2997101.png"
BASE_URL = "http://localhost:8000"
PROJECT = "testproject"


def test_knn_endpoint():
    # Submit the KNN job
    url = f"{BASE_URL}/knn/3/{PROJECT}"
    headers = {"accept": "application/json"}

    with open(IMAGE_PATH, "rb") as f:
        files = {"files": ("7e28463e-bab3-5279-b5ea-a741c2997101.png", f, "image/png")}
        response = requests.post(url, headers=headers, files=files)

    assert response.status_code == 200, f"POST /knn failed: {response.status_code} {response.text}"
    data = response.json()
    assert "job_id" in data, f"Missing job_id in response: {data}"
    job_id = data["job_id"]
    print(f"Submitted KNN job: {job_id}")

    # Wait 5 seconds
    print("Waiting 5 seconds...")
    time.sleep(5)

    # Poll for the result
    poll_url = f"{BASE_URL}/predict/job/{job_id}/{PROJECT}"
    poll_response = requests.get(poll_url)
    assert poll_response.status_code == 200, f"GET job failed: {poll_response.status_code}"

    poll_data = poll_response.json()
    print(f"Job status: {poll_data.get('status', 'unknown')}")

    if poll_data.get("status") == "done":
        result = poll_data.get("result")
        print("Job completed successfully!")
        print(f"Result: {result}")
    elif poll_data.get("status") == "failed":
        print(f"Job failed: {poll_data}")
        assert False, "Job failed"
    else:
        print(f"Job not yet complete. Status: {poll_data.get('status')}")
        print(f"Full response: {poll_data}")


if __name__ == "__main__":
    test_knn_endpoint()
