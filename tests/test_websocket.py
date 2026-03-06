# fastapi-vss, Apache-2.0 license
# Filename: tests/test_websocket.py
# Description: Tests for WebSocket job status endpoint
import json
from unittest.mock import MagicMock, patch

import pytest
from starlette.testclient import TestClient

import sys
sys.path.append("src")

def _make_job(finished=False, failed=False, return_val=None):
    job = MagicMock()
    job.is_finished = finished
    job.is_failed = failed
    job.return_value.return_value = return_val
    return job

@pytest.fixture()
def client():
    """Return a TestClient with mocked Redis / RQ internals."""
    with (
        patch("app.main.config", {"testproject": {"redis_host": "localhost", "redis_port": 6379, "device": "cpu"}}),
        patch("app.main.connections", {"testproject": MagicMock()}),
        patch("app.main.queues", {"testproject": MagicMock()}),
        patch("app.main.DEFAULT_PROJECT", "testproject"),
    ):
        from app.main import app  # import after patches are applied
        yield TestClient(app)

class TestWebSocketJobResult:

    def test_invalid_project(self, client):
        with client.websocket_connect("/ws/predict/job/some-job-id/bad-project") as ws:
            msg = json.loads(ws.receive_text())
        assert msg["status"] == "error"
        assert "Invalid project" in msg["message"]

    def test_job_not_found(self, client):
        with (
            patch("app.main.Job.exists", return_value=False),
        ):
            with client.websocket_connect("/ws/predict/job/missing-id/testproject") as ws:
                msg = json.loads(ws.receive_text())
        assert msg["status"] == "error"
        assert "does not exist" in msg["message"]

    def test_job_finished_immediately(self, client):
        finished_job = _make_job(finished=True, return_val={"scores": [0.9]})
        with (
            patch("app.main.Job.exists", return_value=True),
            patch("app.main.Job.fetch", return_value=finished_job),
        ):
            with client.websocket_connect("/ws/predict/job/done-id/testproject") as ws:
                msg = json.loads(ws.receive_text())
        assert msg["status"] == "done"
        assert msg["result"] == {"scores": [0.9]}

    def test_job_failed(self, client):
        failed_job = _make_job(failed=True)
        with (
            patch("app.main.Job.exists", return_value=True),
            patch("app.main.Job.fetch", return_value=failed_job),
        ):
            with client.websocket_connect("/ws/predict/job/failed-id/testproject") as ws:
                msg = json.loads(ws.receive_text())
        assert msg["status"] == "failed"

    def test_job_pending_then_done(self, client):
        """Job starts pending, then becomes finished on the second poll."""
        pending_job = _make_job(finished=False, failed=False)
        finished_job = _make_job(finished=True, return_val={"scores": [0.8]})

        fetch_side_effects = [pending_job, finished_job]

        with (
            patch("app.main.Job.exists", return_value=True),
            patch("app.main.Job.fetch", side_effect=fetch_side_effects),
            patch("app.main.WS_POLL_INTERVAL", 0),  # no sleep in tests
        ):
            with client.websocket_connect("/ws/predict/job/slow-id/testproject") as ws:
                first = json.loads(ws.receive_text())
                second = json.loads(ws.receive_text())

        assert first["status"] == "pending"
        assert second["status"] == "done"
        assert second["result"] == {"scores": [0.8]}

    def test_embedding_job_result(self, client):
        """Test that embedding results are properly returned."""
        embedding_result = {
            "filenames": ["test.jpg"],
            "embeddings": [[0.1] * 768]
        }
        finished_job = _make_job(finished=True, return_val=embedding_result)

        with (
            patch("app.main.Job.exists", return_value=True),
            patch("app.main.Job.fetch", return_value=finished_job),
        ):
            with client.websocket_connect("/ws/predict/job/embed-id/testproject") as ws:
                msg = json.loads(ws.receive_text())

        assert msg["status"] == "done"
        assert msg["result"]["filenames"] == ["test.jpg"]
        assert len(msg["result"]["embeddings"]) == 1
        assert len(msg["result"]["embeddings"][0]) == 768

    def test_multiple_pending_updates(self, client):
        """Job sends multiple pending updates before completing."""
        pending_job = _make_job(finished=False, failed=False)
        finished_job = _make_job(finished=True, return_val={"predictions": [["A", "B"]]})

        fetch_side_effects = [pending_job, pending_job, pending_job, finished_job]

        with (
            patch("app.main.Job.exists", return_value=True),
            patch("app.main.Job.fetch", side_effect=fetch_side_effects),
            patch("app.main.WS_POLL_INTERVAL", 0),
        ):
            with client.websocket_connect("/ws/predict/job/multi-id/testproject") as ws:
                messages = []
                for _ in range(4):
                    messages.append(json.loads(ws.receive_text()))

        assert messages[0]["status"] == "pending"
        assert messages[1]["status"] == "pending"
        assert messages[2]["status"] == "pending"
        assert messages[3]["status"] == "done"
        assert messages[3]["result"] == {"predictions": [["A", "B"]]}


if __name__ == "__main__":
    pytest.main()