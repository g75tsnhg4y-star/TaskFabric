# TaskFabric | Distributed Asynchronous Job Queue

An enterprise-grade, horizontally scalable background job queue built with Python, FastAPI, and Redis. Designed to handle heavy asynchronous workloads (like quantitative backtesting and ML model inference) by decoupling the API layer from the execution layer.

## 🏗️ System Architecture

TaskFabric implements a classic Producer-Consumer distributed system, allowing the application to process thousands of heavy jobs without blocking the main web server.

*   **Producer API (FastAPI):** A high-throughput REST API that receives job requests, validates payloads, and immediately pushes them to the message broker.
*   **Message Broker (Redis):** Utilizes Redis Lists (`LPUSH` and `BRPOP`) to maintain a strict, fault-tolerant FIFO queue. Task state and metadata are tracked using Redis Hashes.
*   **Consumer Nodes (Python Workers):** Independent worker containers that continuously poll the broker. They utilize blocking pops (`BRPOP`) to consume 0% CPU while idle, instantly waking up when a task is available.
*   **Orchestration (Docker Compose):** The entire microservice matrix (Redis + API + N Worker Nodes) is containerized and orchestrated via Docker, allowing for infinite horizontal scaling of worker nodes based on computational demand.

## 🧠 Engineering Highlights

1.  **Decoupled Workloads:** Prevented API timeouts by strictly separating job ingestion from job execution. The API responds in <5ms regardless of task complexity.
2.  **Concurrency & Scaling:** Deployed multiple independent worker containers that concurrently pull from the same central broker without data duplication or race conditions.
3.  **Fault Tolerance:** Implemented robust try/catch exception handling at the worker level. If a specific task throws a fatal error or contains corrupted data, the isolated worker catches the failure, logs it, and immediately grabs the next task without crashing the container.

## 🚀 How to Run Locally

You can spin up the entire distributed cluster (API + Redis + Multiple Workers) using Docker.

```bash
# Clone the repository
git clone https://github.com/g75tsnhg4y-star/TaskFabric.git
cd TaskFabric

# Boot the cluster
docker-compose up --build
