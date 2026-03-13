from datetime import datetime

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────
# Shared sub-models
# ──────────────────────────────────────────────

class Palette(BaseModel):
    primary: str = Field(default="#0A0A0A", pattern=r"^#[0-9A-Fa-f]{6}$")
    accent1: str = Field(default="#00E5FF", pattern=r"^#[0-9A-Fa-f]{6}$")
    accent2: str = Field(default="#8B5CF6", pattern=r"^#[0-9A-Fa-f]{6}$")
    text_color: str = Field(default="#F5F0EB", pattern=r"^#[0-9A-Fa-f]{6}$")
    bg_color: str = Field(default="#0A0A0A", pattern=r"^#[0-9A-Fa-f]{6}$")


class FontStyle(BaseModel):
    size: int = Field(default=72, ge=12, le=200)
    weight: str = Field(default="bold")
    shadow: bool = Field(default=True)
    position: str = Field(default="center", pattern=r"^(center|top_third|bottom_third)$")


# ──────────────────────────────────────────────
# Personas
# ──────────────────────────────────────────────

class PersonaCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: str | None = Field(default=None, max_length=500)
    prompt_image_base: str = Field(..., min_length=1, max_length=2000)
    prompt_image_variations: list[str] = Field(default_factory=list)
    prompt_video: str = Field(..., min_length=1, max_length=1000)
    negative_prompt: str = Field(default="", max_length=1000)
    palette: Palette = Field(default_factory=Palette)
    font_family: str = Field(default="Bebas Neue")
    font_style: FontStyle = Field(default_factory=FontStyle)
    style_notes: str | None = Field(default=None, max_length=1000)


class PersonaUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=50)
    description: str | None = Field(default=None, max_length=500)
    prompt_image_base: str | None = Field(default=None, min_length=1, max_length=2000)
    prompt_image_variations: list[str] | None = None
    prompt_video: str | None = Field(default=None, min_length=1, max_length=1000)
    negative_prompt: str | None = Field(default=None, max_length=1000)
    palette: Palette | None = None
    font_family: str | None = None
    font_style: FontStyle | None = None
    style_notes: str | None = Field(default=None, max_length=1000)


class PersonaResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    prompt_image_base: str
    prompt_image_variations: list[str] = Field(default_factory=list)
    prompt_video: str
    negative_prompt: str = ""
    palette: Palette
    font_family: str
    font_style: FontStyle
    style_notes: str | None = None
    created_at: datetime
    updated_at: datetime


class PersonaListItem(BaseModel):
    id: str
    name: str
    description: str | None = None
    palette: Palette
    font_family: str
    created_at: datetime
    updated_at: datetime
    job_count: int = 0


class PersonaListResponse(BaseModel):
    data: list[PersonaListItem]
    total: int


# ──────────────────────────────────────────────
# Jobs
# ──────────────────────────────────────────────

class AssetInfo(BaseModel):
    url: str
    type: str


class JobAssets(BaseModel):
    trend: AssetInfo | None = None
    image: AssetInfo | None = None
    video_raw: AssetInfo | None = None
    video_final: AssetInfo | None = None


class JobTimeline(BaseModel):
    created: datetime | None = None
    trend_ready: datetime | None = None
    image_ready: datetime | None = None
    video_ready: datetime | None = None
    complete: datetime | None = None


class JobMetadata(BaseModel):
    image_seed: int | None = None
    video_duration: int | None = None
    generation_cost_usd: float | None = None
    total_time_seconds: float | None = None


class JobListItem(BaseModel):
    id: str
    persona_id: str
    persona_name: str = ""
    type: str
    status: str
    current_step: str | None = None
    hook_text: str
    created_at: datetime
    updated_at: datetime


class JobListResponse(BaseModel):
    data: list[JobListItem]
    total: int
    page: int
    per_page: int


class JobDetailResponse(BaseModel):
    id: str
    persona_id: str
    persona_name: str = ""
    type: str
    status: str
    current_step: str | None = None
    hook_text: str
    trend_url: str | None = None
    assets: JobAssets = Field(default_factory=JobAssets)
    timeline: JobTimeline = Field(default_factory=JobTimeline)
    metadata: JobMetadata = Field(default_factory=JobMetadata)
    error_message: str | None = None
    celery_task_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


# ──────────────────────────────────────────────
# Generate
# ──────────────────────────────────────────────

class GenerateSingleResponse(BaseModel):
    job_id: str
    status: str = "pending"
    message: str = "Job created successfully"


class GenerateBatchResponse(BaseModel):
    batch_id: str
    job_ids: list[str]
    total: int
    status: str = "pending"


# ──────────────────────────────────────────────
# Batch
# ──────────────────────────────────────────────

class BatchDetailResponse(BaseModel):
    id: str
    persona_id: str
    total: int
    completed: int
    failed: int
    running: int = 0
    status: str
    jobs: list[JobListItem] = Field(default_factory=list)


# ──────────────────────────────────────────────
# Library
# ──────────────────────────────────────────────

class LibraryItem(BaseModel):
    id: str
    job_id: str
    persona_id: str
    persona_name: str = ""
    hook_text: str = ""
    public_url: str
    file_size: int | None = None
    mime_type: str
    metadata: dict = Field(default_factory=dict)
    created_at: datetime


class LibraryListResponse(BaseModel):
    data: list[LibraryItem]
    total: int
    page: int
    per_page: int


# ──────────────────────────────────────────────
# Health
# ──────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    redis: str
    supabase: str
    version: str


# ──────────────────────────────────────────────
# Generic
# ──────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: dict = Field(default_factory=dict)
