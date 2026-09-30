from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request


DEFAULT_QUESTIONS = [
    "Can I skip premium payments?",
    "4% 派息率是不是保证的？",
]


def post_json(url: str, payload: dict[str, str]) -> dict[str, object]:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def verify_http(base_url: str, questions: list[str]) -> None:
    chat_url = f"{base_url.rstrip('/')}/api/chat"
    print(f"Verifying running backend at {chat_url}")

    for question in questions:
        result = post_json(chat_url, {"question": question})
        answer = str(result.get("answer", ""))
        citations = result.get("citations", [])
        scope_status = result.get("scope_status")

        if not answer:
            raise AssertionError(f"No answer returned for question: {question}")
        if scope_status == "in_scope" and not citations:
            raise AssertionError(f"In-scope answer has no citations: {question}")

        print(f"OK: {question}")
        print(f"  scope={scope_status}, citations={len(citations)}")


def verify_in_process(questions: list[str]) -> None:
    try:
        from fastapi.testclient import TestClient
        from backend.app.main import app
    except Exception as exc:  # pragma: no cover - developer convenience path
        raise RuntimeError(
            "In-process verification requires backend dependencies. "
            "Install them with: pip install -r backend/requirements.txt"
        ) from exc

    client = TestClient(app)
    print("Verifying backend in process")

    health = client.get("/health")
    health.raise_for_status()

    for question in questions:
        response = client.post("/api/chat", json={"question": question})
        response.raise_for_status()
        result = response.json()
        answer = str(result.get("answer", ""))
        citations = result.get("citations", [])
        scope_status = result.get("scope_status")

        if not answer:
            raise AssertionError(f"No answer returned for question: {question}")
        if scope_status == "in_scope" and not citations:
            raise AssertionError(f"In-scope answer has no citations: {question}")

        print(f"OK: {question}")
        print(f"  scope={scope_status}, citations={len(citations)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke-test the InsureTutor backend.")
    parser.add_argument("--mode", choices=["http", "in-process"], default="http")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--question", action="append", dest="questions")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    questions = args.questions or DEFAULT_QUESTIONS

    try:
        if args.mode == "http":
            verify_http(args.base_url, questions)
        else:
            verify_in_process(questions)
    except urllib.error.URLError as exc:
        print(f"Verification failed: could not reach backend: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Verification failed: {exc}", file=sys.stderr)
        return 1

    print("Verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
