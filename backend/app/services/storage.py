import logging
import os
import time

from app.config import settings
from app.database import supabase

logger = logging.getLogger(__name__)

BUCKET = "assets"


class StorageService:
    """Upload, download, and manage files in Supabase Storage."""

    def upload(
        self,
        file_bytes: bytes,
        persona_id: str,
        job_id: str,
        asset_type: str,
        extension: str,
        mime_type: str,
    ) -> dict:
        """Upload a file to Supabase Storage.

        Returns: {"storage_path": str, "public_url": str, "file_size": int}
        """
        timestamp = int(time.time())
        storage_path = f"{persona_id}/{job_id}/{asset_type}_{timestamp}.{extension}"

        logger.info(
            "Uploading to Supabase Storage",
            extra={
                "job_id": job_id,
                "storage_path": storage_path,
                "file_size": len(file_bytes),
            },
        )

        supabase.storage.from_(BUCKET).upload(
            path=storage_path,
            file=file_bytes,
            file_options={"content-type": mime_type},
        )

        public_url = supabase.storage.from_(BUCKET).get_public_url(storage_path)

        logger.info(
            "Upload complete",
            extra={"job_id": job_id, "storage_path": storage_path},
        )

        return {
            "storage_path": storage_path,
            "public_url": public_url,
            "file_size": len(file_bytes),
        }

    def download(self, storage_path: str) -> bytes:
        """Download a file from Supabase Storage. Returns raw bytes."""
        logger.info("Downloading from Supabase Storage", extra={"storage_path": storage_path})
        data = supabase.storage.from_(BUCKET).download(storage_path)
        logger.info(
            "Download complete",
            extra={"storage_path": storage_path, "file_size": len(data)},
        )
        return data

    def download_to_file(self, storage_path: str, local_path: str) -> str:
        """Download a file from Supabase Storage and save it locally. Returns local path."""
        data = self.download(storage_path)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(data)
        return local_path

    def delete(self, storage_path: str) -> None:
        """Delete a file from Supabase Storage."""
        logger.info("Deleting from Supabase Storage", extra={"storage_path": storage_path})
        supabase.storage.from_(BUCKET).remove([storage_path])

    def get_public_url(self, storage_path: str) -> str:
        """Get the public URL for a file in Supabase Storage."""
        return supabase.storage.from_(BUCKET).get_public_url(storage_path)


def cleanup_temp_dir(job_id: str) -> None:
    """Remove the temporary directory for a job."""
    job_dir = os.path.join(settings.TEMP_DIR, job_id)
    if os.path.exists(job_dir):
        import shutil
        shutil.rmtree(job_dir, ignore_errors=True)
        logger.info("Temp directory cleaned", extra={"job_id": job_id, "path": job_dir})
