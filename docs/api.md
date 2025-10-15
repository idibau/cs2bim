# API

This API provides endpoints to generate IFC models based on polygon input, check the generation state, and retrieve the
generated file.
There is also a swagger documentation site documenting all endpoints: http://0.0.0.0:8000/docs

## Endpoints

### 1. `POST /generate-model/`

**Description:** Starts the generation of a new IFC model.

**Request Body (JSON):**

- `IFC_VERSION` *(string, required)*: The IFC version (`IFC4`, `IFC4X3_ADD2`).
- `NAME` *(string, required)*: The name of the model.
- `POLYGON` *(string, required)*: A closed polygon in WKT (Well-Known Text) format.
- `PROJECT_ORIGIN` *(string, optional)*: Origin point as a comma-separated string `[x,y,z]`.
- `LANGUAGE` *(string, optional)*: The language of the model (`DE`, `FR`, `IT`)

**Responses:**

- `200`: Model generation started successfully. Returns task ID.
- `422`: Validation error in the input data.
- `500`: Error.

---

### 2. `GET /generation-state/{task_id}`

**Description:** Retrieves the current state of a model generation task.

**Path Parameter:**

- `task_id` *(string, required)*: The ID of the generation task.

**Responses:**

- `200`: Returns the state of the task.
- `422`: Validation error.
- `500`: Error.

---

### 3. `GET /generated-file/{task_id}`

**Description:** Fetches the generated IFC file once the task is completed.

**Path Parameter:**

- `task_id` *(string, required)*: The ID of the generation task.

**Responses:**

- `200`: Returns the generated file.
- `202`: Task is still ongoing.
- `400`: Model generation failed.
- `410`: File not found.
- `422`: Validation error.
- `500`: Error.