# StateSync

**Open-source national data synchronization infrastructure**

StateSync demonstrates how government ministries can securely share citizen data without direct database access, while giving citizens full visibility into who accesses their information. Inspired by Estonia's [X-Road](https://x-road.global/), designed to work for any country.

## Why This Matters

Most governments store citizen data in isolated silos. When you need a document from one ministry, they often ask you to bring a paper certificate from another ministry — wasting your time and theirs. Worse, you have no idea who has accessed your data or why.

StateSync solves both problems:

1. **Ministries share data through a secure gateway** — no direct database access, ever
2. **Every access is logged in an immutable audit trail** — citizens see exactly who viewed their data and when
3. **Citizens can report errors** — if your data is wrong, you can flag it directly

## Architecture

```
+-------------------------------------------------------------+
|                      Citizen Portal                         |
|                    (React + TypeScript)                      |
|                      localhost:3000                          |
+-----------------------------+-------------------------------+
                              | HTTP
+-----------------------------v-------------------------------+
|                        API Gateway                          |
|                         (FastAPI)                           |
|                       localhost:8000                         |
|   +-----------+  +-------------+  +-------------------+    |
|   | Citizens  |  | Audit Log   |  |   Redis Cache     |    |
|   | (master)  |  | (immutable) |  |                   |    |
|   +-----------+  +-------------+  +-------------------+    |
+--------+----------------+----------------+-----------------+
         | HTTP            | HTTP           | HTTP
+--------v------+  +------v--------+  +----v-----------+
| Ministry of   |  | Ministry of   |  | Ministry of    |
| Civil Status  |  | Education     |  | Defense        |
| :8001         |  | :8002         |  | :8003          |
| +-----------+ |  | +-----------+ |  | +------------+ |
| | PostgreSQL| |  | | PostgreSQL| |  | | PostgreSQL | |
| +-----------+ |  | +-----------+ |  | +------------+ |
+---------------+  +---------------+  +----------------+
```

**Key principle:** No ministry ever accesses another ministry's database. All communication flows through the gateway via HTTP.

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)

### Run

```bash
docker-compose up --build
```

Then open:

| Service             | URL                          |
|---------------------|------------------------------|
| Citizen Portal      | http://localhost:3001         |
| Gateway API docs    | http://localhost:8080/docs    |
| Ministry Civil      | http://localhost:8001/docs    |
| Ministry Education  | http://localhost:8002/docs    |
| Ministry Defense    | http://localhost:8003/docs    |

### Demo CINs

The system ships with seed data. Try these CINs in the portal:

| CIN        | Name          |
|------------|---------------|
| `12345678` | John Smith    |
| `87654321` | Maria Garcia  |
| `11223344` | Yuki Tanaka   |

## API Reference

| Method | Endpoint                  | Description                              |
|--------|---------------------------|------------------------------------------|
| GET    | `/citizen/{cin}`          | Aggregated data from all ministries      |
| GET    | `/citizen/{cin}/audit`    | Immutable audit trail                    |
| POST   | `/citizen/{cin}/report`   | Report an error in citizen data          |
| POST   | `/ministry/{name}/update` | Ministry pushes a data update            |
| GET    | `/health`                 | Health check                             |
| POST   | `/auth/token`             | Generate a demo JWT token                |

## How to Add a New Ministry

1. **Copy an existing ministry:**
   ```bash
   cp -r ministry-civil ministry-health
   ```

2. **Create the database schema** — add `db/init-health.sql`:
   ```sql
   CREATE TABLE IF NOT EXISTS health_records (
       cin             VARCHAR(20) PRIMARY KEY,
       blood_type      VARCHAR(5),
       allergies       JSONB DEFAULT '[]'::jsonb,
       created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
       updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );
   ```

3. **Update the ORM model** in `ministry-health/app/models.py`

4. **Update the routes** in `ministry-health/app/main.py` with the new fields

5. **Add services to `docker-compose.yml`:**
   ```yaml
   postgres-health:
     image: postgres:16-alpine
     environment:
       POSTGRES_USER: statesync
       POSTGRES_PASSWORD: statesync_secret
       POSTGRES_DB: health_db
     volumes:
       - ./db/init-health.sql:/docker-entrypoint-initdb.d/init.sql
     healthcheck:
       test: ["CMD-SHELL", "pg_isready -U statesync -d health_db"]
       interval: 5s
       timeout: 3s
       retries: 5

   ministry-health:
     build: ./ministry-health
     ports:
       - "8004:8004"
     environment:
       DATABASE_URL: postgresql://statesync:statesync_secret@postgres-health:5432/health_db
     depends_on:
       postgres-health:
         condition: service_healthy
   ```

6. **Register in the gateway** — add the URL to the `MINISTRIES` dict in `gateway/app/main.py` and `gateway/app/config.py`

7. **Update the frontend** — add types in `citizen-portal/src/types/index.ts` and a display section in `CitizenData.tsx`

## Project Structure

```
StateSync/
├── docker-compose.yml
├── gateway/                    # Central API gateway
│   └── app/
│       ├── main.py             # Routes & aggregation logic
│       ├── models.py           # Citizens + AuditLog ORM
│       ├── auth.py             # JWT handling
│       ├── database.py         # SQLAlchemy setup
│       └── config.py           # Environment config
├── ministry-civil/             # Civil status microservice
├── ministry-education/         # Education microservice
├── ministry-defense/           # Defense microservice
├── citizen-portal/             # React + TypeScript + Tailwind
│   └── src/
│       ├── App.tsx
│       ├── api/client.ts
│       ├── components/
│       └── types/index.ts
└── db/                         # Database init scripts (with seed data)
    ├── init-gateway.sql
    ├── init-civil.sql
    ├── init-education.sql
    └── init-defense.sql
```

## Core Principles

- **No direct database access** — ministries communicate only through the gateway
- **Immutable audit log** — database rules prevent UPDATE and DELETE on audit entries
- **Citizen transparency** — citizens see all data the state holds about them
- **Error reporting** — citizens can flag incorrect data
- **Country-agnostic** — designed to work for any country

## Tech Stack

| Component      | Technology                    |
|----------------|-------------------------------|
| API Gateway    | FastAPI (Python)              |
| Microservices  | FastAPI (Python)              |
| Frontend       | React + TypeScript + Tailwind |
| Database       | PostgreSQL 16                 |
| Cache          | Redis 7                       |
| Auth           | JWT (python-jose)             |
| Containers     | Docker + Docker Compose       |

## Roadmap

- [ ] mTLS between services for inter-service authentication
- [ ] Real citizen authentication (eID, OAuth2)
- [ ] Ministry admin dashboards
- [ ] Async event bus (NATS / RabbitMQ)
- [ ] Blockchain-anchored audit hashes
- [ ] Rate limiting and API throttling
- [ ] Multi-language citizen portal (i18n)
- [ ] Data export for citizens (GDPR compliance)
- [ ] End-to-end encryption between services
- [ ] Prometheus + Grafana monitoring

## License

MIT
