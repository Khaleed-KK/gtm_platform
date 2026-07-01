# 📊 Platform-Wide GTM Market Intelligence & ROI Tracker

An automated, self-sustaining B2B SaaS intelligence engine that tracks competitor YouTube metrics over time, computes algorithmic proxy marketing funnels, and leverages the Gemini Pro Engine to generate high-CTR video assets based on real-time data contrast.

---

## 🏗️ System Architecture & Workflow

The platform shifts away from stateless keyword scraping into a production-grade **Time-Series Tracking Ledger** and a modular execution stack:

```text
               +---------------------------------------+
               |         Orchestrator (run.py)         |
               +-------------------+-------------------+
                                   |
         +-------------------------+-------------------------+
         |                                                   |
         v                                                   v
+------------------------+                          +------------------------+
| Background Event Loop  |                          |  Streamlit Frontend    |
| (pipeline/worker.py)   |                          |   (app/dashboard.py)   |
+-----------+------------+                          +-----------+------------+
            |                                                   ^
            v                                                   |
+------------------------+                                      |
| Ingestion & Analytics  |                                      |
| (pipeline/ingestion.py)|                                      |
+-----------+------------+                                      |
            |                                                   |
            v                                                   |
+------------------------+      +-------------------+           |
|  Gemini AI Strategy    |----> |   Neon Postgres   |-----------+
| (pipeline/ai_engine.py)|      |  (Cloud Database) |
+------------------------+      +-------------------+
```

1. **Process Orchestration (`run.py`)**: A master bootloader that programmatically spins up the background worker and the user interface simultaneously under a single Python process, eliminating zombie/orphaned threads upon shutdown.
2. **Resilient Telemetry Daemon (`pipeline/worker.py`)**: An infinite background event loop configured to capture snapshots. Built with robust high-level error boundaries to naturally absorb transient network spikes or SSL dropouts without crashing the system.
3. **Data Ingestion Matrix (`pipeline/ingestion.py`)**: Resolves public handles (e.g., `@HubSpot-CRM`) down to low-level Channel IDs, pulls recent upload feeds, logs rolling metric drift, and dispatches targeted payloads to the AI tier.
4. **Context-Aware Strategy Engine (`pipeline/ai_engine.py`)**: Programmed via prompt engineering to act as an elite YouTube content strategist, using analytical data contrast to output ready-to-publish video titles instead of abstract corporate advice.
5. **Analytics UI (`app/dashboard.py`)**: Uses high-performance PostgreSQL Common Table Expressions (CTEs) to isolate historical snapshots and render calculated pipeline financial projections instantly.

---

## 📂 Project Repository Layout

```text
catalyst_gtm_platform/
│
├── app/
│   └── dashboard.py          # Streamlit UI Analytics & Financial ROI Projections
│
├── core/
│   └── database.py           # Neon Serverless PostgreSQL Connection Manager
│
├── pipeline/
│   ├── ai_engine.py          # Gemini AI Prompt Layer & Competitive Data Evaluator
│   ├── ingestion.py          # Core Data Ingest, Handle Resolver, & DB Commits
│   └── worker.py             # Self-Healing Background Scheduler Daemon Loop
│
├── .env.example              # Structural Key & DB Endpoint Template Configuration
├── requirements.txt          # Explicit Production Package Environment Manifest
└── run.py                    # Master Multi-Process Orchestrator Script
```

---

## ⚡ Quickstart Deployment Guide

### 1. Environment Setup
Clone the repository and install the production package manifest inside your local python environment:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a real `.env` file in the root directory based on the configuration layout within `.env.example`:
```env
YOUTUBE_API_KEY=your_actual_youtube_api_key_here
GEMINI_API_KEY=your_actual_gemini_api_key_here
DATABASE_URL=postgresql://user:password@neon_host/dbname?sslmode=require
```

### 3. Initialize Neon Database Schema
Execute the following structural script inside your Neon SQL Editor console to drop old mock layouts and generate the indexed relational time-series architecture:

```sql
DROP TABLE IF EXISTS video_metrics_snapshots CASCADE;
DROP TABLE IF EXISTS videos CASCADE;
DROP TABLE IF EXISTS recommendations CASCADE;

CREATE TABLE videos (
    video_id VARCHAR(50) PRIMARY KEY,
    channel_title VARCHAR(255),
    title TEXT,
    published_at TIMESTAMP,
    topic VARCHAR(100),
    format VARCHAR(100)
);

CREATE TABLE video_metrics_snapshots (
    snapshot_id SERIAL PRIMARY KEY,
    video_id VARCHAR(50) REFERENCES videos(video_id) ON DELETE CASCADE,
    view_count INT,
    like_count INT,
    comment_count INT,
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE recommendations (
    rec_id SERIAL PRIMARY KEY,
    topic VARCHAR(100),
    format VARCHAR(100),
    angle TEXT,
    reasoning TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metrics_video_timestamp ON video_metrics_snapshots (video_id, captured_at DESC);
```

### 4. Boot the Ecosystem (Single Terminal Command)
Activate both the telemetry daemon and the client-facing analytical application frame simultaneously with one command:
```bash
python3 run.py
```

---

## 💎 Engineering Highlights

> **Fault-Resilient Architecture**: The ingestion stream uses explicit try/except matrices within its scheduled worker loop. If a Google API threshold limit or an external network socket closure occurs, the core engine blocks data corruption, preserves active tables, waits, and self-heals during the next cycle.

> **Optimized Analytical Queries**: The Streamlit user interface references a high-performance PostgreSQL Common Table Expression (`WITH latest_snapshots AS... DISTINCT ON (video_id)`). This completely avoids database aggregation multipliers, ensuring sub-millisecond calculation speeds regardless of historical dataset depth.
