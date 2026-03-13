# Skill: FFmpeg + Pillow (Text Overlay)

## Workflow overlay

```
1. Pillow : Générer une image PNG transparente avec le texte
2. FFmpeg : Overlay l'image PNG sur la vidéo
3. FFmpeg : Export MP4 H.264 sans watermark
```

## Service (overlay.py)

```python
import subprocess
import os
from PIL import Image, ImageDraw, ImageFont
from app.config import settings

class OverlayService:
    def __init__(self):
        self.fonts_dir = os.path.join(os.path.dirname(__file__), "../../assets/fonts")
    
    def create_text_image(self, text: str, width: int, height: int, font_family: str, font_style: dict, palette: dict) -> str:
        """Crée une image PNG transparente avec le text overlay."""
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Charger la font
        font_path = os.path.join(self.fonts_dir, f"{font_family}.ttf")
        if not os.path.exists(font_path):
            font_path = os.path.join(self.fonts_dir, "Arial.ttf")  # fallback
        font = ImageFont.truetype(font_path, font_style.get("size", 72))
        
        # Texte en majuscules
        text_upper = text.upper()
        
        # Calculer la position
        bbox = draw.textbbox((0, 0), text_upper, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        position = font_style.get("position", "center")
        x = (width - text_width) // 2
        if position == "center":
            y = (height - text_height) // 2
        elif position == "top_third":
            y = height // 3 - text_height // 2
        else:  # bottom_third
            y = 2 * height // 3 - text_height // 2
        
        # Ombre si activée
        if font_style.get("shadow", True):
            shadow_offset = max(2, font_style.get("size", 72) // 20)
            draw.text((x + shadow_offset, y + shadow_offset), text_upper, font=font, fill=(0, 0, 0, 180))
        
        # Texte principal
        text_color = palette.get("text_color", "#F5F0EB")
        draw.text((x, y), text_upper, font=font, fill=text_color)
        
        output_path = f"{settings.TEMP_DIR}/overlay_{os.getpid()}.png"
        img.save(output_path, "PNG")
        return output_path
    
    def apply_overlay(self, video_path: str, overlay_path: str, output_path: str) -> str:
        """Applique l'overlay PNG sur la vidéo via FFmpeg."""
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", overlay_path,
            "-filter_complex", "[0:v][1:v]overlay=0:0",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-an",  # pas d'audio
            "-movflags", "+faststart",
            output_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            raise Exception(f"FFmpeg failed: {result.stderr}")
        return output_path
```

## Règles
- Toujours exporter SANS audio (`-an`) — l'audio est ajouté manuellement dans l'app TikTok/YouTube/IG
- Toujours `yuv420p` (compatibilité maximale)
- Toujours `-movflags +faststart` (streaming-friendly)
- Toujours nettoyer les fichiers temp après upload vers Supabase
- La font doit être un .ttf dans `assets/fonts/`. Ne pas compter sur les fonts système.
- Texte toujours en MAJUSCULES (voir VISUAL_GUIDE dans la bible)
