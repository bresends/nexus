# Nexus — System Architecture

Nexus is a personal project management system with AI-powered information evaluation. It tracks projects, tasks, and learning resources, and integrates with an external YouTube filtering pipeline to capture study material without noise.

---

## Stack

| Layer | Technology |
|---|---|
| Web framework | Flask 3.x |
| ORM | SQLAlchemy 2.x |
| Migrations | Alembic |
| Database | PostgreSQL (Supabase in production) |
| Deployment | Fly.io (`nexuslab`, region: São Paulo) |
| Package manager | uv |
| LLM providers | Anthropic, OpenAI, DeepSeek, GitHub Models |
| Observability | Langfuse |

---

## Project Structure

```
nexus/
├── src/
│   ├── app.py                  # Flask app factory + entry point
│   ├── main.py                 # CLI pipeline entry point
│   ├── api/
│   │   └── routes.py           # All Flask routes (single blueprint)
│   ├── models/                 # SQLAlchemy models
│   │   ├── project.py
│   │   ├── task.py
│   │   ├── resource.py
│   │   ├── video_log.py
│   │   └── video_evaluation_dataset.py
│   ├── database/
│   │   └── database.py         # Engine, session, Base
│   ├── services/
│   │   └── llm_factory.py      # Multi-provider LLM abstraction
│   ├── pipelines/
│   │   └── pkm/                # AI evaluation pipelines
│   ├── prompts/
│   │   ├── prompt_manager.py   # Jinja2 template loader
│   │   └── templates/          # .j2 prompt templates
│   ├── utils/
│   │   ├── markdown_helper.py  # Markdown → safe HTML
│   │   └── calculator.py
│   ├── templates/              # HTML (Jinja2)
│   └── static/                 # CSS (BEM), JS (vanilla)
├── alembic/                    # Migrations
├── docs/                       # This directory
├── tests/
├── Dockerfile
└── fly.toml
```

---

## Data Model

```
projects
  │
  └─── tasks (1:N)
         │
         └─── resources (1:N)
                  ▲
                  │ resource_id (nullable FK)
video_log ────────┘
```

### projects

| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | |
| `name` | String(255) | |
| `purpose` | Text | Why the project exists |
| `description` | Text | What it covers |
| `desired_outcome` | Text | What done looks like |
| `status` | String(50) | e.g. `Planning`, `In Progress`, `Completed` |
| `priority` | String(50) | `low`, `normal`, `high` |
| `is_active` | Boolean | Max 2 projects active at once |
| `deadline` | DateTime | Optional |
| `created_at` / `updated_at` | DateTime | Auto-managed |

### tasks

| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | |
| `project_id` | FK → projects | |
| `name` | String(255) | |
| `description` | Text | |
| `context` | Text | Additional context for AI evaluation |
| `status` | String(50) | `todo`, `in progress`, `done` |
| `priority` | String(50) | `low`, `medium`, `high` |
| `sort_order` | Integer | Drag-and-drop ordering |
| `due_date` | DateTime | Optional |

### resources

Genuine learning materials attached to a task — videos, articles, papers.

| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | |
| `task_id` | FK → tasks | |
| `title` | String(255) | Format: `(Channel) - Title` for videos |
| `url` | String(255) | UNIQUE — natural dedup key |
| `type` | String(50) | `video`, `article`, `paper` |
| `notes` | Text | Summary or key takeaways |
| `is_consumed` | Boolean | True = actually watched/read |
| `sort_order` | Integer | Ordering within task |
| `added_at` | DateTime | |

### video_log

Audit log of every video URL ever evaluated by the pipeline. The dedup layer — keeps the resources table clean.

| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | |
| `url` | String(500) | UNIQUE — dedup key |
| `title` | String(255) | |
| `verdict` | String(20) | `filed`, `skipped`, `graveyard` |
| `source` | String(20) | `pipeline`, `telegram`, `manual` |
| `notes` | Text | Filter score, rejection reason, summary |
| `profile_used` | String(255) | Knowledge profile name used for filtering |
| `resource_id` | FK → resources | Set when verdict = `filed` |
| `logged_at` | DateTime | |

**Why this exists:** A skipped video is not a resource — it's a triage decision. Forcing it into `resources` produced dishonest data (`is_consumed: true` on unwatched videos). `video_log` separates the two bounded contexts cleanly.

---

## Web Interface

Single Flask blueprint (`projects_bp`) registered in `app.py`. All routes serve HTML via Jinja2 templates. Some routes return partial HTML for HTMX-style updates (e.g., `toggle-consumed`).

### Routes summary

```
GET  /                                       → redirect to /projects
GET  /projects                               → active projects (is_active = true)
GET  /projects/archived                      → inactive projects

GET  /projects/<id>                          → project detail + task list
POST /projects/<id>/toggle-active            → toggle active (max 2 limit enforced)
POST /projects/create
POST /projects/<id>/update
POST /projects/<id>/delete/confirm

GET  /projects/<id>/tasks/<task_id>          → task detail + resources
POST /projects/<id>/tasks/add
POST /projects/<id>/tasks/<task_id>/update
POST /projects/<id>/tasks/reorder            → JSON: drag-and-drop reorder
POST /projects/<id>/tasks/<task_id>/delete/confirm

POST /tasks/<task_id>/resources/reorder      → JSON: drag-and-drop reorder
POST /resources/<resource_id>/toggle-consumed → returns HTML badge
POST /resources/<resource_id>/update
POST /resources/<resource_id>/delete

GET  /projects/<id>/json                     → export single project
GET  /projects/all/json                      → export all projects
```

### Active project limit

Only 2 projects can have `is_active = true` at a time. The dashboard shows only active projects; the rest are in the archive. This enforces focus.

---

## AI Evaluation Pipeline

### NewProjectInfoEvaluatorPipeline

`src/pipelines/pkm/new_info_for_project_evaluator.py`

Evaluates whether a piece of new information is relevant to an existing project. Used via the CLI (`uv run src/main.py`, reads from `input.txt`).

**Output** (`NewInfoClassification`):
- `relevance`: `no_relevance`, `weak_relevance`, `strong_relevance`
- `novelty`: `new`, `redundant`, `partially_redundant`
- `action`: `add_to_project`, `exclude`

### LLM Factory

`src/services/llm_factory.py` — abstracts 5 providers:

| Provider | Default model |
|---|---|
| Anthropic | claude-3-5-sonnet |
| OpenAI | gpt-4o |
| DeepSeek | deepseek-chat |
| GitHub Models | gpt-4.1-mini |
| Llama | llama3 (local) |

Uses `instructor` for structured output parsing and `langfuse` for tracing.

---

## YouTube Video Pipeline (External)

The pipeline lives outside this repo in an Obsidian Claude Code skill (`filtering-youtube-videos`). It writes to this database via `nexus_db.py` (a standalone psycopg2 script that mirrors the core DB operations without requiring the Flask app).

### Flow

```
YouTube URL
    │
    ▼
check-url → video_log (then fallback: resources)
    │
 Found? ──YES──► "Already processed: [verdict]" → STOP
    │
   NO
    ▼
Gemini filter analysis against knowledge profile
    │
 SKIP ──────────► log-video (verdict=skipped) → STOP
    │
 WATCH/SKIM
    │
    ▼
Update knowledge profile (Obsidian Markdown)
    │
    ▼
Match to project → task
    │
    ▼
add-resource → returns resource_id
    │
    ▼
log-video (verdict=filed, resource_id=...)
```

### How a video is discarded

When the filter returns SKIP and the user confirms:

1. `log-video` writes to `video_log` with `verdict='skipped'`, the URL, score, and reason
2. No resource is created, no project/task matching happens
3. Next time that URL enters the pipeline, `check-url` finds the `video_log` entry and stops immediately — the filter never runs again

The rejection reason is preserved in `notes`, so you always know *why* something was skipped.

---

## Running Locally

```bash
# Start dev server
uv run src/app.py   # runs on 0.0.0.0:5000

# Run migrations
uv run alembic upgrade head

# Run AI evaluation pipeline
uv run src/main.py  # reads from input.txt in project root
```

## Deployment

Push to `main` → GitHub Actions → `flyctl deploy --remote-only` → Fly.io (`nexuslab`, São Paulo).

Force HTTPS enabled. Min 1 machine always running.
