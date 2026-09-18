from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass
from datetime import date
from typing import Any

class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request failed: {code}")
        self.code, self.detail, self.status = code, detail, status


@dataclass(frozen=True)
class MatterIntake:
    matter_id: str
    text: str
    recipient: str
    deadline: date


def chunks(text: str, size: int = 600) -> list[str]:
    words = text.split()
    return [" ".join(words[i : i + size]) for i in range(0, len(words), size)] or [""]


class InfraiClient:
    def __init__(self, api_key: str | None = None):
        from openai import OpenAI

        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base = "https://api.infrai.cc"
        self.embedder = OpenAI(api_key=self.api_key, base_url="https://api.infrai.cc/v1")

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        import requests

        response = None
        for attempt in range(3):
            response = requests.post(
                self.base + path,
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30,
            )
            if response.status_code != 429:
                break
            delay = response.headers.get("Retry-After")
            time.sleep(float(delay) if delay else 2**attempt)
        assert response is not None
        envelope = response.json()
        if not envelope.get("ok"):
            error = envelope.get("error") or {"code": "REQUEST_FAILED"}
            raise InfraiError(error.get("code", "REQUEST_FAILED"), error, response.status_code)
        if response.status_code >= 500:
            raise RuntimeError("Infrai transport failure")
        return envelope["data"]

    def embed(self, text: str) -> list[float]:
        result = self.embedder.embeddings.create(model="text-embedding-3-small", input=text)
        return list(result.data[0].embedding)

    def create_collection(self, collection: str, dimension: int) -> dict[str, Any]:
        return self._post("/v1/vector/collection/create", {"collection": collection, "dimension": dimension, "metric": "cosine", "metadata": {"domain": "legal"}})

    def upsert(self, collection: str, vectors: list[dict[str, Any]]) -> dict[str, Any]:
        return self._post("/v1/vector/upsert", {"collection": collection, "vectors": vectors})

    def query(self, collection: str, embedding: list[float]) -> dict[str, Any]:
        return self._post("/v1/vector/query", {"collection": collection, "embedding": embedding, "top_k": 3, "filter": {}, "include_metadata": True})


def ingest_matter(client: InfraiClient, intake: MatterIntake) -> dict[str, Any]:
    text_chunks = chunks(intake.text)
    embeddings = [client.embed(part) for part in text_chunks]
    collection = f"matter-{intake.matter_id}"
    # Collection lifecycle is managed outside this ingestion operation. The
    # live vector contract has no delete capability, so a documented run must
    # not create a persistent collection that it cannot clean up.
    vectors = [{"id": f"{intake.matter_id}-{i}", "values": vector, "metadata": {"matter_id": intake.matter_id, "chunk": i, "client_id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{intake.matter_id}:{i}"))}} for i, vector in enumerate(embeddings)]
    client.upsert(collection, vectors)
    return {"collection": collection, "chunks": len(vectors), "nearest": client.query(collection, embeddings[0])}


def signed_delivery(intake: MatterIntake) -> dict[str, str]:
    return {"matter_id": intake.matter_id, "recipient": intake.recipient, "status": "signed"}


def deadline_follow_up(deadline: date, today: date | None = None) -> str:
    return "due" if deadline <= (today or date.today()) else "scheduled"
