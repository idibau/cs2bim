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
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Request {func.__name__} failed: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    return wrapper


@router.post("/generate-model/")
@log_exceptions
async def generate_model(request_data: GenerateModelRequest):
    ifc_version = request_data.IFC_VERSION
    name = request_data.NAME
    polygon = request_data.POLYGON

    project_origin = None
    if request_data.PROJECT_ORIGIN:
        try:
            string_values = request_data.PROJECT_ORIGIN.split(",")
            project_origin = tuple(map(float, string_values))
        except ValueError:
            raise HTTPException(status_code=422, detail="PROJECT_ORIGIN parameter must be in format float,float,float")

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

    task = model_generation_task.delay(ifc_version.value, name, polygon, project_origin)
    return {"task_id": task.id}


@router.get("/generation-state/{task_id}")
@log_exceptions
async def get_generation_state(task_id: str):
    result = AsyncResult(task_id, app=app)

    state = result.state

    response = {"state": state}

    if state == "FAILURE":
        response["error"] = str(result.result)

    return response


@router.get("/generated-file/{task_id}")
@log_exceptions
async def get_generated_file(task_id: str):
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
