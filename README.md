# StateSync

**Open-source national data synchronization platform**

> The state knows everything about the citizen — not the citizen proving things to the state.
> Citizens see all their data and who accessed it. Zero paper. Zero corruption.

Inspired by Estonia's [X-Road](https://x-road.global/), designed to work for **any country**.

---

## Vision

Most governments store citizen data in isolated silos. When you need a document, you physically visit one ministry, wait in line, get a paper certificate, then carry it to another ministry. You have no idea who has accessed your data or why.

**StateSync eliminates this entirely:**

- Citizens access ALL their government data from one portal
- Request services, get official documents — no ministry visit needed
- Life events ("getting married") trigger ALL related paperwork automatically
- Every data access is logged in an immutable, blockchain-anchored audit trail
- Citizens control who sees their data via consent-based sharing
- Emergency health access saves lives

---

## Architecture

```
                         +-------------------+
                         |  Citizen Portal   |
                         |  React+TS+Tailwind|
                         |  localhost:3001   |
                         +--------+----------+
                                  |
                    +-------------v--------------+
                    |       API Gateway          |
                    |        (FastAPI)            |
                    |      localhost:8080         |
                    |                            |
                    |  +--------+ +----------+   |
                    |  |Citizens| |Audit Log |   |
                    |  |(master)| |(immutable)|  |
                    |  +--------+ +----------+   |
                    |  +--------+ +----------+   |
                    |  |Services| |Documents |   |
                    |  |Requests| |Generated |   |
                    |  +--------+ +----------+   |
                    |  +--------+ +----------+   |
                    |  | Shares | |Blockchain|   |
                    |  | & Auth | | Anchors  |   |
                    |  +--------+ +----------+   |
                    |       + Redis Cache         |
                    +--+----+----+----+----+-----+
                       |    |    |    |    |
            +----------+    |    |    |    +----------+
            |          +----+    |    +----+          |
     +------v---+ +----v---+ +--v----+ +---v----+ +--v------+
     |  Civil   | |  Edu   | |Health | |Finance | |  ...    |
     |  :8001   | | :8002  | | :8004 | | :8006  | | 9 total |
     | +------+ | |+------+| |+-----+| |+------+| |         |
     | |PgSQL | | ||PgSQL || ||PgSQL|| ||PgSQL || |         |
     | +------+ | |+------+| |+-----+| |+------+| |         |
     +----------+ +--------+ +-------+ +--------+ +---------+
```

**Key principle:** No ministry ever accesses another ministry's database. All communication flows through the gateway. The access control matrix determines which ministry can read which other ministry's data.

### Access Control Matrix

| Ministry | Can Read |
|----------|----------|
| Health | Civil, Social |
| Finance | Civil, Social, Property |
| Justice | Civil, Transport |
| Transport | Civil, Justice |
| Social | Civil, Finance |
| Education | Civil |
| Defense | Civil, Health |
| Property | Civil, Finance |

Citizens can read **ALL** their own data. Ministries can only **UPDATE** their own data.

---

## Features (22 delivered across 5 phases)

### Phase 1 — Core Services
- **Life Events Engine** — 7 workflows (marriage, baby, university, retirement, business, property, bereavement). "Getting married" auto-triggers 6 steps across civil, justice, health
- **Document Bundles** — 6 pre-packaged sets (Job Application, Bank Loan, Travel, University, Business, Retirement). One click = multiple official documents
- **QR Code Verification** — Every PDF document embeds a scannable QR code
- **Public Verification Portal** — Anyone can verify a document's authenticity without login

### Phase 2 — Smart Experience
- **Smart Assistant** — Context-aware slide-out panel. Analyzes citizen data and suggests services, life events, and actions. Detects benefit eligibility, expired documents, tax issues
- **Proactive Reminders** — Auto-generated alerts: expired license, unpaid fines, vaccination due, child benefit eligibility, retirement approaching
- **Completeness Score** — Profile completeness ring (0-100%) with per-field checklist across all ministries

### Phase 3 — Real-time & Trust
- **WebSocket Notifications** — Real-time push when data is accessed, requests approved, emergencies triggered
- **Consent Management** — Citizens create scoped, time-limited share links. Choose which ministries to share, set expiry, one-time access. Revoke anytime
- **Emergency Access Protocol** — Hospitals get blood type, allergies, chronic diseases instantly. Bypasses auth. Logged as EMERGENCY. Citizen notified

### Phase 4 — Platform & Scale
- **Delegation System** — Authorize spouse, lawyer, or parent to act on your behalf with scoped access
- **Appointment Booking** — Book ministry office visits. 70+ slots across civil, transport, justice. Cancel/reschedule online
- **Analytics Dashboard** — System-wide metrics, per-ministry stats, request breakdown charts
- **Third-Party API** — Banks and hospitals integrate via API keys with scoped access and rate limiting

### Phase 5 — Polish & Security
- **Dark Mode** — Full dark theme, persisted toggle
- **Multi-language** — English, French, Arabic (RTL support). Language switcher, translated navigation
- **PWA** — Installable on mobile, offline-capable with service worker
- **Blockchain Audit Anchoring** — Merkle tree hashing of audit entries. Mathematical proof of tamper-proof history

---

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)

### Run

```bash
git clone https://github.com/hammdi/StateSync.git
cd StateSync
docker-compose up --build -d
```

Then open:

| Service | URL |
|---------|-----|
| Citizen Portal | http://localhost:3001 |
| Gateway API (Swagger) | http://localhost:8080/docs |

### 10 Demo Citizens

| CIN | Name | Profile |
|-----|------|---------|
| `10000001` | Ahmed El Fassi | Engineer, married, 2 kids, mortgage |
| `10000002` | Maria Santos | Doctor, cardiology resident |
| `10000003` | John Mitchell | CEO, 3 companies, 3 properties, high income |
| `10000004` | Aisha Patel | Teacher, child benefit |
| `10000005` | Youssef Karim | Retired colonel, disability pension, 28yr military |
| `10000006` | Lin Chen | Student, scholarships, deferred military |
| `10000007` | David Rousseau | Lawyer, divorced, traffic violations, tax pending |
| `10000008` | Amina Diallo | Nurse, organ donor, 2 kids |
| `10000009` | Carlos Mendoza | Farmer, widowed, 5ha land, expired license |
| `10000010` | Sophie Andersson | Software dev, expat, Tesla owner |

### Demo Credentials

**Employee Portal** (click "Ministry Staff Login" on landing page):

| Username | Password | Ministry |
|----------|----------|----------|
| `civil.agent` | `admin123` | Civil Status |
| `finance.agent` | `admin123` | Finance |
| `admin` | `admin123` | All (admin) |

**Third-Party API Keys:**

| Organization | API Key | Scopes |
|-------------|---------|--------|
| National Bank | `sk_test_statesync_bank` | civil, finance, property |
| City Hospital | `sk_hosp_statesync_hospital` | civil, health |

```bash
# Example: Bank accesses citizen finance data
curl "http://localhost:8080/api/v1/citizen/10000003?api_key=sk_test_statesync_bank"
```

### OTP Authentication

OTP codes are printed to the gateway console:

```bash
# Request OTP
curl -X POST http://localhost:8080/auth/otp/request \
  -H "Content-Type: application/json" \
  -d '{"cin":"10000001"}'

# Check gateway logs for the code
docker-compose logs gateway | grep OTP
```

---

## API Reference

### Public (no auth)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Gateway health check |
| GET | `/ministries` | List all ministries + status + access matrix |
| GET | `/public/verify/{reference}` | Verify document authenticity |
| GET | `/services` | Full service catalog (33 services) |
| GET | `/life-events` | List life event workflows |
| GET | `/bundles` | List document bundles |

### Citizen (OTP auth)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/otp/request` | Request OTP code |
| POST | `/auth/otp/verify` | Verify OTP, get JWT |
| GET | `/citizen/{cin}` | All data from all ministries |
| GET | `/citizen/{cin}/audit` | Full audit trail |
| GET | `/citizen/{cin}/{ministry}` | Specific ministry data |
| GET | `/citizen/{cin}/completeness` | Profile completeness score |
| GET | `/citizen/{cin}/reminders` | Smart alerts & reminders |
| GET | `/citizen/{cin}/assistant` | AI suggestions |
| POST | `/citizen/{cin}/report-error` | Report incorrect data |
| GET | `/citizen/{cin}/error-reports` | Track error reports |

### Services & Documents
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/requests` | Submit service request |
| GET | `/requests/{cin}` | List citizen's requests |
| POST | `/bundles/{id}?cin=X` | Request document bundle |
| POST | `/life-events/{id}?cin=X` | Start life event workflow |
| GET | `/documents/{cin}` | List generated documents |
| GET | `/documents/{cin}/{id}` | Document content (JSON) |
| GET | `/documents/{cin}/{id}/pdf` | Download as PDF (with QR) |

### Consent & Sharing
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/shares` | Create scoped share link |
| GET | `/shares/{cin}` | List active shares |
| DELETE | `/shares/{cin}/{token}` | Revoke a share |
| POST | `/public/shared/{token}?access_code=X` | Access shared data |

### Delegation
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/delegations` | Create delegation |
| GET | `/delegations/{cin}` | List given/received delegations |
| GET | `/delegations/{cin}/act-as/{target}` | Delegate views citizen data |
| DELETE | `/delegations/{cin}/{id}` | Revoke delegation |

### Appointments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/appointments/slots?ministry=X` | Available slots |
| POST | `/appointments` | Book appointment |
| GET | `/appointments/{cin}` | My appointments |
| DELETE | `/appointments/{cin}/{id}` | Cancel appointment |

### Emergency
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/emergency/{cin}` | Emergency health data (doctor+hospital required) |

### Employee Portal (JWT)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/employee/login` | Employee authentication |
| GET | `/employee/dashboard` | Stats + pending queue |
| GET | `/employee/requests?status=X` | Filter requests |
| PUT | `/employee/requests/{id}` | Approve/reject request |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/stats` | System-wide statistics |
| GET | `/admin/error-reports` | Pending error reports |
| PUT | `/admin/error-reports/{id}` | Resolve error report |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics/overview` | System metrics + charts |
| GET | `/analytics/ministry/{name}` | Per-ministry stats |

### Blockchain
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/audit/anchor` | Create Merkle anchor (admin) |
| GET | `/audit/chain` | View blockchain |
| GET | `/audit/verify/{block}` | Verify block integrity |

### Third-Party API
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/citizen/{cin}?api_key=X` | Scoped citizen data |
| GET | `/api/v1/verify/{ref}?api_key=X` | Verify document |

---

## 9 Ministry Microservices

| Ministry | Port | Data Fields |
|----------|------|-------------|
| Civil Status | :8001 | address, city, marital status, children, parents, death date |
| Education | :8002 | diplomas, equivalences, scholarships, current enrollment |
| Defense | :8003 | military status, service dates, unit, rank, exemption |
| Health | :8004 | blood type, allergies, chronic diseases, vaccinations, disabilities, organ donor |
| Justice | :8005 | criminal record, cases, sentences, restrictions |
| Finance | :8006 | tax ID, tax status, declarations, fines, company ownerships |
| Social Affairs | :8007 | SS number, employment history, pension points, contributions, benefits |
| Transport | :8009 | driving license, vehicles, traffic violations, technical inspections |
| Property | :8011 | properties, mortgages, land registry |

Each ministry has its own PostgreSQL database, Dockerfile, FastAPI service, and SQLAlchemy models.

---

## How to Add a New Ministry

1. **Copy an existing ministry:**
   ```bash
   cp -r ministry-civil ministry-newname
   ```

2. **Create the database schema** in `db/init-newname.sql`

3. **Update the models** in `ministry-newname/app/models.py`

4. **Update the routes** in `ministry-newname/app/main.py`

5. **Add to `docker-compose.yml`** — postgres instance + ministry service

6. **Register in the gateway:**
   - `gateway/app/config.py` — add URL
   - `gateway/app/main.py` — add to MINISTRIES dict
   - `gateway/app/access_control.py` — add to access matrix

7. **Update the frontend** — types + display component

---

## Project Structure

```
StateSync/
+-- docker-compose.yml              # 22 containers orchestration
+-- gateway/                         # Central API gateway
|   +-- app/
|       +-- main.py                  # 1600+ lines, all endpoints
|       +-- models.py                # 15 ORM models
|       +-- access_control.py        # Ministry access matrix
|       +-- auth.py                  # JWT + OTP
|       +-- smart_assistant.py       # AI suggestions + reminders
|       +-- services_catalog.py      # 33 government services
|       +-- bundles_catalog.py       # 6 bundles + 7 life events
|       +-- document_generator.py    # Official document templates
|       +-- pdf_generator.py         # PDF with QR codes
|       +-- blockchain.py            # Merkle tree anchoring
|       +-- config.py                # Environment settings
|       +-- database.py              # SQLAlchemy setup
+-- ministry-civil/                  # 9 ministry microservices
+-- ministry-education/              #   each with: Dockerfile,
+-- ministry-defense/                #   app/main.py, models.py,
+-- ministry-health/                 #   config.py, database.py
+-- ministry-justice/
+-- ministry-finance/
+-- ministry-social/
+-- ministry-transport/
+-- ministry-property/
+-- citizen-portal/                  # React frontend
|   +-- public/
|   |   +-- manifest.json            # PWA manifest
|   |   +-- sw.js                    # Service worker
|   +-- src/
|       +-- App.tsx                  # Main app + routing
|       +-- i18n/translations.ts     # EN/FR/AR translations
|       +-- api/client.ts            # API client
|       +-- components/
|           +-- Dashboard.tsx        # Stats + alerts + completeness
|           +-- LifeEventsPage.tsx   # Life event workflows
|           +-- BundlesPage.tsx      # Document bundles
|           +-- ServicesPage.tsx     # 33 services catalog
|           +-- RequestsPage.tsx     # Request tracking + PDF viewer
|           +-- DataSharingPage.tsx  # Consent management
|           +-- AppointmentsPage.tsx # Booking system
|           +-- AnalyticsPage.tsx    # System analytics
|           +-- AssistantPanel.tsx   # Smart assistant
|           +-- CompletenessCard.tsx # Profile completeness
|           +-- EmployeePortal.tsx   # Employee dashboard
|           +-- VerifyPage.tsx       # Public verification
|           +-- CitizenData.tsx      # Ministry data display
|           +-- AuditTrail.tsx       # Timeline audit log
|           +-- ErrorReport.tsx      # Error reporting
|           +-- Header.tsx           # Navigation + controls
|           +-- SearchBar.tsx        # CIN search
+-- db/                              # SQL init scripts (10 files)
    +-- init-gateway.sql             # 200+ lines, all gateway tables
    +-- init-civil.sql               # 10 citizens per ministry
    +-- init-education.sql
    +-- init-defense.sql
    +-- init-health.sql
    +-- init-justice.sql
    +-- init-finance.sql
    +-- init-social.sql
    +-- init-transport.sql
    +-- init-property.sql
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| API Gateway | FastAPI (Python 3.12) |
| Microservices | FastAPI (Python 3.12) |
| Frontend | React 18 + TypeScript + Tailwind CSS |
| Database | PostgreSQL 15 (one per ministry) |
| Cache | Redis 7 |
| Auth | JWT + OTP (phone verification) |
| Documents | PDF generation (fpdf2) + QR codes |
| Blockchain | Merkle tree (SHA-256) |
| Real-time | WebSocket |
| i18n | EN / FR / AR (RTL) |
| PWA | Service Worker + manifest |
| Containers | Docker + Docker Compose |

---

## Comparison with Estonia's X-Road

| Feature | Estonia X-Road | StateSync |
|---------|---------------|-----------|
| Inter-ministry data exchange | Yes | Yes |
| Citizen data portal | eesti.ee | Citizen Portal |
| Audit trail | Yes | Yes + blockchain anchoring |
| Document generation | Limited | Full PDF with QR |
| Life event workflows | Partial | 7 automated workflows |
| Emergency health access | No | Yes |
| Consent-based sharing | Limited | Full (scoped, time-limited) |
| Smart assistant | No | AI-powered suggestions |
| Third-party API | Yes | Yes (scoped API keys) |
| Mobile PWA | No | Yes |
| Multi-language | Estonian/English | EN/FR/AR (RTL) |

---

## Roadmap

- [x] 9 ministry microservices with rich data models
- [x] 10 realistic citizens with comprehensive seed data
- [x] Access control matrix
- [x] OTP citizen authentication
- [x] 33 online government services
- [x] PDF document generation with QR codes
- [x] Life events engine (7 workflows)
- [x] Document bundles (6 packs)
- [x] Smart assistant with proactive reminders
- [x] Consent-based data sharing
- [x] Emergency health access protocol
- [x] Delegation system
- [x] Appointment booking
- [x] Analytics dashboard
- [x] Third-party API with rate limiting
- [x] Dark mode
- [x] Multi-language (EN/FR/AR + RTL)
- [x] PWA (installable, offline)
- [x] Blockchain audit anchoring
- [x] Employee portal with approve/reject
- [x] Public document verification
- [x] WebSocket real-time notifications
- [ ] mTLS between services
- [ ] Async event bus (NATS/RabbitMQ)
- [ ] Prometheus + Grafana monitoring
- [ ] E2E encryption
- [ ] Biometric authentication
- [ ] SMS gateway integration (production OTP)

---

## License

MIT
