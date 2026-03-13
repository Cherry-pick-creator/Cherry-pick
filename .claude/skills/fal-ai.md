# Skill: fal.ai (FLUX + Kling)

## Client (fal_client.py)

```python
import httpx
import time
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class FalClient:
    BASE_URL = "https://fal.run"
    QUEUE_URL = "https://queue.fal.run"
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Key {settings.FAL_KEY}",
            "Content-Type": "application/json",
        }
    
    def generate_image(self, prompt: str, negative_prompt: str = "", seed: int | None = None) -> dict:
        """Appel synchrone FLUX. Retourne {"url": str, "seed": int}."""
        payload = {
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
        
        with httpx.Client(timeout=60) as client:
            response = client.post(f"{self.BASE_URL}/fal-ai/flux-pro/v1.1", headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return {"url": data["images"][0]["url"], "seed": data.get("seed")}
    
    def generate_video(self, prompt: str, image_url: str, video_url: str, negative_prompt: str = "", duration: int = 5) -> dict:
        """Appel asynchrone Kling. Submit → poll → result. Retourne {"url": str, "seed": int}."""
        payload = {
            "prompt": prompt,
            "image_url": image_url,
            "video_url": video_url,
            "duration": duration,
            "aspect_ratio": "9:16",
        }
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        
        endpoint = "fal-ai/kling-video/v2.6/standard/motion-control"
        
        # 1. Submit
        with httpx.Client(timeout=30) as client:
            response = client.post(f"{self.QUEUE_URL}/{endpoint}", headers=self.headers, json=payload)
            response.raise_for_status()
            request_id = response.json()["request_id"]
        
        # 2. Poll
        for _ in range(60):  # max 10 min (60 × 10s)
            time.sleep(10)
            with httpx.Client(timeout=10) as client:
                response = client.get(f"{self.QUEUE_URL}/{endpoint}/requests/{request_id}/status", headers=self.headers)
                status_data = response.json()
                if status_data["status"] == "COMPLETED":
                    break
                if status_data["status"] == "FAILED":
                    raise Exception(f"Kling generation failed: {status_data}")
        else:
            raise TimeoutError("Kling generation timed out after 10 minutes")
        
        # 3. Get result
        with httpx.Client(timeout=30) as client:
            response = client.get(f"{self.QUEUE_URL}/{endpoint}/requests/{request_id}", headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return {"url": data["video"]["url"], "seed": data.get("seed")}
```

## Règles
- httpx (pas requests) — meilleur pour les timeouts
- Toujours logger les appels avec durée
- Ne JAMAIS stocker les URLs fal.ai en dur — elles expirent. Toujours télécharger et re-upload vers Supabase.
- Le polling Kling bloque le worker Celery pendant 3-6 min → c'est normal, c'est pourquoi on a une queue `generation` dédiée
