import logging

from celery import chain, group

from app.celery_app import celery
from app.tasks.download_trend import download_trend
from app.tasks.generate_image import generate_image
from app.tasks.generate_video import generate_video
from app.tasks.postprod import postprod

logger = logging.getLogger(__name__)


def run_pipeline_single(
    job_id: str,
    persona_id: str,
    trend_source: str,
    trend_url: str | None,
    trend_storage_path: str | None,
    image_variation: int | None,
    video_duration: int,
    hook_text: str,
    font_override: dict | None,
) -> str:
    """Launch the full 4-task chain for a single video generation.

    Returns the Celery chain task ID.
    """
    logger.info("Launching pipeline_single", extra={"job_id": job_id, "persona_id": persona_id})

    task_chain = chain(
        download_trend.s(
            job_id=job_id,
            trend_source=trend_source,
            trend_url=trend_url,
            trend_storage_path=trend_storage_path,
        ),
        generate_image.s(
            job_id=job_id,
            persona_id=persona_id,
            image_variation=image_variation,
        ),
        generate_video.s(
            job_id=job_id,
            persona_id=persona_id,
            video_duration=video_duration,
        ),
        postprod.s(
            job_id=job_id,
            persona_id=persona_id,
            hook_text=hook_text,
            font_override=font_override,
        ),
    )

    result = task_chain.apply_async()
    return result.id


def run_pipeline_batch(
    batch_id: str,
    persona_id: str,
    jobs_config: list[dict],
) -> list[str]:
    """Launch N pipeline_single chains in parallel via Celery group.

    jobs_config: list of dicts with keys:
        job_id, trend_source, trend_url, trend_storage_path,
        image_variation, video_duration, hook_text, font_override

    Returns list of Celery task IDs.
    """
    logger.info(
        "Launching pipeline_batch",
        extra={"batch_id": batch_id, "persona_id": persona_id, "count": len(jobs_config)},
    )

    chains = []
    task_ids = []

    for config in jobs_config:
        task_chain = chain(
            download_trend.s(
                job_id=config["job_id"],
                trend_source=config["trend_source"],
                trend_url=config.get("trend_url"),
                trend_storage_path=config.get("trend_storage_path"),
            ),
            generate_image.s(
                job_id=config["job_id"],
                persona_id=persona_id,
                image_variation=config.get("image_variation"),
            ),
            generate_video.s(
                job_id=config["job_id"],
                persona_id=persona_id,
                video_duration=config.get("video_duration", 5),
            ),
            postprod.s(
                job_id=config["job_id"],
                persona_id=persona_id,
                hook_text=config["hook_text"],
                font_override=config.get("font_override"),
            ),
        )
        chains.append(task_chain)

    result = group(chains).apply_async()

    for child in result.children:
        task_ids.append(child.id)

    return task_ids
