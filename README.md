# ProtoScript

ProtoScript is a high-performance, asynchronous REST service designed to convert multi-channel audio recordings (FLAC) into structured meeting protocols based on metadata. It is built with Django, Celery, and Hugging Face's Transformers.

This project is part of the **OneLiteFeatherNET** ecosystem.

## Features

- **Asynchronous Processing**: Uses a Request-Result pattern to handle long-running transcription tasks.
- **Speech-to-Text**: Integrated with Hugging Face's Whisper models for high-quality transcription.
- **Multi-channel Support**: Maps audio channels to specific users based on provided metadata.
- **Flexible Templating**: Uses Jinja2 templates (e.g., Markdown, Discord-flavored Markdown) for protocol generation.
- **Cloud-Native Storage**: Uses S3-compatible storage for audio files, metadata, and results.
- **Scalable Architecture**: Decoupled API and Worker nodes, supporting RabbitMQ or other Celery brokers.
- **OpenAPI Documentation**: Automatically generated Swagger UI and ReDoc documentation.
- **Production Ready**: Containerized with Docker and includes Kubernetes deployment manifests.

## Architecture

ProtoScript is designed as a modular monolith:
- **API**: Handles file uploads, job creation, and status polling.
- **Worker**: Processes the audio, performs transcription, and renders the final protocol.
- **Core**: Contains the shared logic for STT engines, S3 interaction, and protocol rendering.

No relational database is required for production; all state is managed via S3-compatible storage.

## Getting Started

### Prerequisites

- [uv](https://github.com/astral-sh/uv) (for dependency management)
- Docker and Docker Compose

### Local Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/OneLiteFeatherNET/ProtoScript.git
   cd ProtoScript
   ```

2. **Start Infrastructure**:
   Start the local RabbitMQ and S3 Mock (using `adobe/s3mock`):
   ```bash
   docker-compose up -d
   ```

3. **Install Dependencies**:
   ```bash
   uv sync
   ```

4. **Configure Environment**:
   Create a `.env` file based on the provided examples:
   ```env
   STT_ENGINE=whisper
   STT_MODEL=openai/whisper-tiny
   CELERY_BROKER_URL=amqp://guest:guest@localhost:5673//
   S3_ENDPOINT_URL=http://localhost:9091
   S3_BUCKET_NAME=protoscript-protocols
   S3_ACCESS_KEY=test
   S3_SECRET_KEY=test
   ```

5. **Run the API**:
   ```bash
   python manage.py runserver 8008
   ```

6. **Run the Worker**:
   ```bash
   celery -A ProtoScript worker --loglevel=info
   ```

### Running with Docker

Build and run the container:
```bash
docker build -t protoscript .
docker run -p 8008:8008 --env-file .env protoscript
```

## API Documentation

Once the server is running, you can access the interactive documentation:

- **Swagger UI**: [http://localhost:8008/api/protocols/schema/swagger-ui/](http://localhost:8008/api/protocols/schema/swagger-ui/)
- **ReDoc**: [http://localhost:8008/api/protocols/schema/redoc/](http://localhost:8008/api/protocols/schema/redoc/)

## Usage Flow

1. **POST `/api/protocols/request/`**: Upload `meta.json` and `audio.flac`. Receive a `job_id`.
2. **GET `/api/protocols/result/<job_id>/`**: Poll the status. Once `status` is `completed`, the `result_markdown` field will contain the protocol.

## Cleanup

To clean up old jobs from S3, run the management command:
```bash
python manage.py cleanup_jobs --minutes 60
```

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

Developed for **OneLiteFeatherNET**.
