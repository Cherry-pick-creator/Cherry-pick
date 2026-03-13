import logging
import time

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class FalClient:
    """Client for fal.ai API calls (FLUX image generation + Kling video generation)."""

    BASE_URL = "https://fal.run"
    QUEUE_URL = "https://queue.fal.run"

    def __init__(self) -> None:
        self.headers = {
            "Authorization": f"Key {settings.FAL_KEY}",
            "Content-Type": "application/json",
        }

    def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        seed: int | None = None,
    ) -> dict:
        """Generate an image via FLUX 1.1 Pro (synchronous, ~10-30s).

        Returns: {"url": str, "seed": int}
        """
        payload: dict = {
            "prompt": prompt,
            "image_size": {"width": 768, "height": 1344},
            "num_images": 1,
            "guidance_scale": 7.5,
            "num_inference_steps": 28,
            "safety_tolerance": "5",
        }
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        if seed is not None:
            payload["seed"] = seed

        logger.info(
            "Calling fal.ai FLUX",
            extra={"prompt_length": len(prompt), "seed": seed},
        )
        start = time.monotonic()

        with httpx.Client(timeout=60) as client:
            response = client.post(
                f"{self.BASE_URL}/fal-ai/flux-pro/v1.1",
                headers=self.headers,
                json=payload,
            )
            self._handle_http_error(response, "FLUX")
            data = response.json()

        elapsed = round(time.monotonic() - start, 2)
        image_url = data["images"][0]["url"]
        result_seed = data.get("seed")
        logger.info(
            "FLUX image generated",
            extra={"elapsed_s": elapsed, "seed": result_seed},
        )
        return {"url": image_url, "seed": result_seed}

    def generate_video(
        self,
        prompt: str,
        image_url: str,
        video_url: str,
        negative_prompt: str = "",
        duration: int = 5,
    ) -> dict:
        """Generate a video via Kling v2.6 Motion Control (async: submit -> poll -> result, ~3-6min).

        Returns: {"url": str, "seed": int}
        """
        payload: dict = {
            "prompt": prompt,
            "image_url": image_url,
            "video_url": video_url,
            "duration": duration,
            "aspect_ratio": "9:16",
        }
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt

        endpoint = "fal-ai/kling-video/v2.6/standard/motion-control"

        # Step 1 — Submit
        logger.info(
            "Submitting Kling video generation",
            extra={"duration": duration, "prompt_length": len(prompt)},
        )
        with httpx.Client(timeout=30) as client:
            response = client.post(
                f"{self.QUEUE_URL}/{endpoint}",
                headers=self.headers,
                json=payload,
            )
            self._handle_http_error(response, "Kling submit")
            request_id = response.json()["request_id"]

        logger.info("Kling request submitted", extra={"request_id": request_id})

        # Step 2 — Poll (max 60 iterations x 10s = 10 min)
        start = time.monotonic()
        for poll_count in range(60):
            time.sleep(10)
            with httpx.Client(timeout=10) as client:
                response = client.get(
                    f"{self.QUEUE_URL}/{endpoint}/requests/{request_id}/status",
                    headers=self.headers,
                )
                status_data = response.json()
                status = status_data.get("status", "UNKNOWN")

                logger.info(
                    "Kling poll",
                    extra={
                        "request_id": request_id,
                        "poll": poll_count + 1,
                        "status": status,
                        "queue_position": status_data.get("queue_position"),
                    },
                )

                if status == "COMPLETED":
                    break
                if status == "FAILED":
                    raise FalKlingError(
                        f"Kling generation failed: {status_data.get('error', 'unknown')}"
                    )
        else:
            raise FalTimeoutError("Kling generation timed out after 10 minutes")

        # Step 3 — Get result
        with httpx.Client(timeout=30) as client:
            response = client.get(
                f"{self.QUEUE_URL}/{endpoint}/requests/{request_id}",
                headers=self.headers,
            )
            self._handle_http_error(response, "Kling result")
            data = response.json()

        elapsed = round(time.monotonic() - start, 2)
        video_result_url = data["video"]["url"]
        result_seed = data.get("seed")
        logger.info(
            "Kling video generated",
            extra={"elapsed_s": elapsed, "request_id": request_id, "seed": result_seed},
        )
        return {"url": video_result_url, "seed": result_seed}

    def download_file(self, url: str) -> bytes:
        """Download a file from a fal.ai URL (images/videos expire, must re-upload)."""
        with httpx.Client(timeout=120) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.content

    @staticmethod
    def _handle_http_error(response: httpx.Response, context: str) -> None:
        """Raise typed exceptions for fal.ai HTTP errors."""
        if response.status_code == 422:
            raise FalSafetyError(f"{context}: prompt rejected by safety filter")
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", "60")
            raise FalRateLimitError(
                f"{context}: rate limit exceeded (retry after {retry_after}s)"
            )
        response.raise_for_status()


# ── Typed exceptions ──────────────────────────

class FalError(Exception):
    """Base exception for fal.ai errors."""


class FalSafetyError(FalError):
    """Prompt rejected by safety filter."""


class FalRateLimitError(FalError):
    """Rate limit exceeded."""


class FalTimeoutError(FalError):
    """Generation timed out."""


class FalKlingError(FalError):
    """Kling generation failed."""
