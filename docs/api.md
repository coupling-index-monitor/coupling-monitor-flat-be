# API Documentation

## Traces

### Get All Traces
- **Endpoint:** `/api/traces`
- **Method:** `GET`
- **Description:** Retrieve all traces from the MongoDB collection.
- **Response:**
  - `status`: success
  - `traces`: List of all trace documents

### Get Traces by Parent Service
- **Endpoint:** `/api/traces/services/{service}`
- **Method:** `GET`
- **Description:** Retrieve traces where the parent service matches the given name.
- **Parameters:**
  - `service` (path): The name of the parent service.
- **Response:**
  - `status`: success
  - `traces`: List of traces matching the criteria

## Graphs

### Create Dependency Graph
- **Endpoint:** `/api/graphs/create`
- **Method:** `POST`
- **Description:** Create or update the dependency graph using new traces.
- **Response:**
  - `status`: success or error
  - `message`: Details about the operation

### Fetch Dependency Graph
- **Endpoint:** `/api/graphs`
- **Method:** `GET`
- **Description:** Fetch the dependency graph as JSON data.
- **Response:**
  - `status`: success or error
  - `graph`: JSON-compatible data of the dependency graph

## Services

### Get All Services
- **Endpoint:** `/api/services`
- **Method:** `GET`
- **Description:** Retrieve all available services.
- **Response:**
  - `status`: success
  - `services`: List of all service names

## Coupling

### Get Absolute Importance of a Service
- **Endpoint:** `/api/coupling/absolute-importance-of`
- **Method:** `GET`
- **Description:** Calculate the Absolute Importance of a Service (AIS).
- **Parameters:**
  - `service` (query, optional): The name of the target service.
- **Response:**
  - `status`: success or error
  - `data`: AIS value or dictionary with service names and their AIS values

### Coupling Health
- **Endpoint:** `/api/coupling`
- **Method:** `GET`
- **Description:** Fetch the dependency graph as JSON data.
- **Response:**
  - `status`: success or error
  - `graph`: JSON-compatible data of the dependency graph