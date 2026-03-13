import logging
import os
import subprocess

from app.config import settings

logger = logging.getLogger(__name__)

# Max trend file size in bytes
MAX_FILE_SIZE = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


class Downloader:
    """Download trend videos via yt-dlp."""

    def __init__(self) -> None:
        self.temp_dir = settings.TEMP_DIR

    def download_trend(self, url: str, job_id: str) -> str:
        """Download a TikTok trend video via yt-dlp.

        Returns the local file path of the downloaded MP4.
        """
        job_dir = os.path.join(self.temp_dir, job_id)
        os.makedirs(job_dir, exist_ok=True)
        output_path = os.path.join(job_dir, "trend.mp4")

        cmd = [
            "yt-dlp",
            "-f", "best[height<=1080]",
            "--no-watermark",
            "--max-filesize", f"{settings.MAX_UPLOAD_SIZE_MB}M",
            "--socket-timeout", "30",
            "--no-check-certificates",
            "-o", output_path,
            url,
        ]

        logger.info(
            "Starting yt-dlp download",
            extra={"job_id": job_id, "url": url},
        )

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )
        except subprocess.TimeoutExpired as exc:
            raise DownloadTimeoutError(f"Download timed out after 60s: {url}") from exc

        if result.returncode != 0:
            stderr = result.stderr.lower()
            if "video unavailable" in stderr or "private" in stderr:
                raise DownloadUnavailableError(f"Video unavailable or private: {url}")
            if "unsupported url" in stderr:
                raise DownloadUnsupportedError(f"Unsupported URL format: {url}")
            raise DownloadError(f"yt-dlp failed (code {result.returncode}): {result.stderr[:500]}")

        if not os.path.exists(output_path):
            raise DownloadError(f"yt-dlp completed but output file not found: {output_path}")

        file_size = os.path.getsize(output_path)
        if file_size > MAX_FILE_SIZE:
            os.remove(output_path)
            raise DownloadFileTooLargeError(
                f"Downloaded file too large: {file_size / 1024 / 1024:.1f}MB > {settings.MAX_UPLOAD_SIZE_MB}MB"
            )

        logger.info(
            "yt-dlp download complete",
            extra={"job_id": job_id, "file_size": file_size, "path": output_path},
        )
        return output_path

    @staticmethod
    def validate_upload(file_bytes: bytes, content_type: str | None) -> None:
        """Validate an uploaded trend file."""
        if content_type and content_type != "video/mp4":
            raise DownloadInvalidFormatError("Only MP4 files are accepted")

        if len(file_bytes) > MAX_FILE_SIZE:
            raise DownloadFileTooLargeError(
                f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB}MB"
            )

    @staticmethod
    def save_upload(file_bytes: bytes, job_id: str) -> str:
        """Save an uploaded trend file to temp dir. Returns local file path."""
        job_dir = os.path.join(settings.TEMP_DIR, job_id)
        os.makedirs(job_dir, exist_ok=True)
        output_path = os.path.join(job_dir, "trend.mp4")

        with open(output_path, "wb") as f:
            f.write(file_bytes)

        logger.info(
            "Upload saved",
            extra={"job_id": job_id, "file_size": len(file_bytes), "path": output_path},
        )
        return output_path


# ── Typed exceptions ──────────────────────────

class DownloadError(Exception):
    """Base exception for download errors."""


class DownloadTimeoutError(DownloadError):
    """Download timed out."""


class DownloadUnavailableError(DownloadError):
    """Video unavailable or private."""


class DownloadUnsupportedError(DownloadError):
    """Unsupported URL format."""


class DownloadFileTooLargeError(DownloadError):
    """File exceeds maximum size."""


class DownloadInvalidFormatError(DownloadError):
    """Invalid file format."""
