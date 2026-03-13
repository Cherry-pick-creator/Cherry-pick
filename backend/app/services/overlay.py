import logging
import os
import subprocess

from PIL import Image, ImageDraw, ImageFont

from app.config import settings

logger = logging.getLogger(__name__)

# Output video dimensions (9:16 portrait)
OUTPUT_WIDTH = 1080
OUTPUT_HEIGHT = 1920


class OverlayService:
    """Apply text overlay on video via Pillow (text image) + FFmpeg (composite)."""

    def __init__(self) -> None:
        self.fonts_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "assets", "fonts"
        )

    def create_text_image(
        self,
        text: str,
        font_family: str,
        font_style: dict,
        palette: dict,
        width: int = OUTPUT_WIDTH,
        height: int = OUTPUT_HEIGHT,
    ) -> str:
        """Create a transparent PNG with the text overlay.

        Returns the path to the generated PNG.
        """
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Load font
        font_size = font_style.get("size", 72)
        font_path = os.path.join(self.fonts_dir, f"{font_family}.ttf")
        if not os.path.exists(font_path):
            logger.warning(
                "Font not found, using fallback",
                extra={"font_family": font_family, "fallback": "Arial"},
            )
            font_path = os.path.join(self.fonts_dir, "Arial.ttf")
            if not os.path.exists(font_path):
                font = ImageFont.load_default()
            else:
                font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.truetype(font_path, font_size)

        # Text always uppercase
        text_upper = text.upper()

        # Word wrap to fit width with margin
        margin = int(width * 0.08)
        max_text_width = width - 2 * margin
        lines = self._wrap_text(draw, text_upper, font, max_text_width)

        # Calculate total text block height
        line_spacing = int(font_size * 0.25)
        line_heights = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_heights.append(bbox[3] - bbox[1])
        total_text_height = sum(line_heights) + line_spacing * (len(lines) - 1)

        # Vertical position
        position = font_style.get("position", "center")
        if position == "top_third":
            y_start = height // 3 - total_text_height // 2
        elif position == "bottom_third":
            y_start = 2 * height // 3 - total_text_height // 2
        else:  # center
            y_start = (height - total_text_height) // 2

        # Draw each line
        text_color = palette.get("text_color", "#F5F0EB")
        shadow_enabled = font_style.get("shadow", True)
        shadow_offset = max(2, font_size // 20)

        y = y_start
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            x = (width - line_width) // 2

            if shadow_enabled:
                draw.text(
                    (x + shadow_offset, y + shadow_offset),
                    line,
                    font=font,
                    fill=(0, 0, 0, 180),
                )

            draw.text((x, y), line, font=font, fill=text_color)
            y += line_heights[i] + line_spacing

        # Save
        os.makedirs(settings.TEMP_DIR, exist_ok=True)
        output_path = os.path.join(settings.TEMP_DIR, f"overlay_{os.getpid()}.png")
        img.save(output_path, "PNG")

        logger.info(
            "Text overlay image created",
            extra={"lines": len(lines), "position": position, "path": output_path},
        )
        return output_path

    def apply_overlay(self, video_path: str, overlay_path: str, output_path: str) -> str:
        """Composite the overlay PNG onto the video via FFmpeg.

        Returns the output MP4 path.
        """
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", overlay_path,
            "-filter_complex", "[0:v][1:v]overlay=0:0",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-an",
            "-movflags", "+faststart",
            output_path,
        ]

        logger.info(
            "Running FFmpeg overlay",
            extra={"video": video_path, "output": output_path},
        )

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        except subprocess.TimeoutExpired as exc:
            raise OverlayError("FFmpeg timed out after 120s") from exc

        if result.returncode != 0:
            raise OverlayError(f"FFmpeg failed: {result.stderr[:500]}")

        logger.info("FFmpeg overlay complete", extra={"output": output_path})
        return output_path

    def process(
        self,
        video_path: str,
        text: str,
        font_family: str,
        font_style: dict,
        palette: dict,
        output_path: str,
    ) -> str:
        """Full pipeline: create text image + overlay on video.

        Returns the final MP4 path.
        """
        overlay_path = self.create_text_image(text, font_family, font_style, palette)
        try:
            return self.apply_overlay(video_path, overlay_path, output_path)
        finally:
            # Clean up overlay PNG
            if os.path.exists(overlay_path):
                os.remove(overlay_path)

    @staticmethod
    def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
        """Word-wrap text to fit within max_width."""
        words = text.split()
        if not words:
            return [text]

        lines: list[str] = []
        current_line = words[0]

        for word in words[1:]:
            test_line = f"{current_line} {word}"
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        lines.append(current_line)
        return lines


# ── Typed exceptions ──────────────────────────

class OverlayError(Exception):
    """FFmpeg/overlay processing failed."""
