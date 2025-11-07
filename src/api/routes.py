import functools
import logging
import os
from celery.result import AsyncResult
from fastapi import HTTPException, APIRouter
from fastapi.responses import FileResponse
from shapely import wkt
from shapely.geometry import Polygon

from api.generate_model_request import GenerateModelRequest
from worker.app import app, model_generation_task

logger = logging.getLogger(__name__)

router = APIRouter()


def log_exceptions(func):
    """
    A function decorator that catches and logs exceptions.

    Args:
        func: The asynchronous function to decorate.

    Returns:
        A decorated function that catches and logs exceptions.

    Raises:
        HTTPException: Passes through HTTPExceptions or converts general exceptions
                       to HTTPExceptions with status 500.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"request {func.__name__} failed: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    return wrapper


@router.post("/generate-model/")
@log_exceptions
async def generate_model(request_data: GenerateModelRequest):
    """
    Initiates a process to generate an ifc model based on a polygon.

    Args:
        request_data: GenerateModelRequest with the required data for model generation.

    Returns:
        A dictionary containing the task_id of the started Celery task.

    Raises:
        HTTPException (422): When PROJECT_ORIGIN is not correctly formatted.
        HTTPException (422): When the POLYGON parameter is not valid.
        HTTPException (500): For other internal errors.
    """

    ifc_version = request_data.IFC_VERSION
    name = request_data.NAME
    polygon = request_data.POLYGON
    language = request_data.LANGUAGE

    project_origin = None
    if request_data.PROJECT_ORIGIN:
        try:
            project_origin = [float(coord.strip()) for coord in request_data.PROJECT_ORIGIN.split(",")]
        except ValueError:
            raise HTTPException(status_code=422,
                                detail="PROJECT_ORIGIN must contain only numbers in the format 'float,float,float' (e.g., 0.0,0.0,0.0).")
        if len(project_origin) != 3:
            raise HTTPException(status_code=422,
                                detail="PROJECT_ORIGIN must contain exactly three values separated by commas (e.g., 0.0,0.0,0.0).")
    try:
        geom = wkt.loads(polygon)
        if not isinstance(geom, Polygon):
            raise HTTPException(status_code=422, detail="POLYGON parameter is not a polygon")
        if not geom.is_valid:
            raise HTTPException(status_code=422, detail="POLYGON parameter is not valid")
        if not geom.exterior.is_ring or not all(interior.is_ring for interior in geom.interiors):
            raise HTTPException(status_code=422, detail="POLYGON parameter is not closed")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"POLYGON parameter could not be parsed: {e}")

    logger.info(
        f"Received generate-model request: IFC_VERSION={ifc_version}, NAME={name}, POLYGON={polygon}, PROJECT_ORIGIN={project_origin if project_origin else 'calculated'}"
    )

    task = model_generation_task.delay(ifc_version.value, name, polygon, project_origin,
                                       language.value if language else None)
    return {"task_id": task.id}


@router.get("/generation-state/{task_id}")
@log_exceptions
async def get_generation_state(task_id: str):
    """
    Returns the current status of a model generation task.

    Args:
        task_id: ID of the Celery task

    Returns:
        A dictionary with the current status of the task and error information if applicable.

    Raises:
        HTTPException (500): For internal errors.
    """

    result = AsyncResult(task_id, app=app)

    state = result.state

    response = {"state": state}

    if state == "FAILURE":
        response["error"] = str(result.result)

    return response


@router.get("/generated-file/{task_id}")
@log_exceptions
async def get_generated_file(task_id: str):
    """
    Returns the generated model file if the task completed successfully.

    Args:
        task_id: ID of the Celery task

    Returns:
        The generated model file as a download.

    Raises:
        HTTPException (202): When the task is still in progress.
        HTTPException (400): When the task failed.
        HTTPException (410): When the generated file cannot be found on disk.
        HTTPException (500): For internal errors.
    """

    result = AsyncResult(task_id, app=app)

    state = result.state

    if state in ["PENDING", "STARTED", "RETRY"]:
        raise HTTPException(
            status_code=202,
            detail=f"Model generation state is {state.lower()}"
        )

    if state == "FAILURE":
        raise HTTPException(
            status_code=400,
            detail=f"Model generation failed: {str(result.result)}"
        )

    output_path = result.result

    if not output_path or not os.path.exists(output_path):
        raise HTTPException(status_code=410, detail="Generated file not found on disk")

    return FileResponse(path=output_path, filename=os.path.basename(output_path), media_type='application/octet-stream')
