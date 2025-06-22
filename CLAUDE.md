# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
- Flask development server: `uv run src/app.py` (runs on 0.0.0.0:5000 with debug enabled)
- Main CLI pipeline: `uv run  src/main.py` (requires input.txt file in root directory)
- Assume the development server is always running. So instead of using uv run src/app.py just ask the user to check for the changes.

### Testing
- Run tests: `pytest` (configured to test from `tests/` and `src/evals/` directories)
- Test paths include both project root and `src/` for imports

### Database Management
- Database migrations are handled via Alembic
- Migration files are in `alembic/versions/`
- Connection via PostgreSQL using `DATABASE_URL` environment variable

## Architecture Overview

### Project Structure
This is a Flask-based project management system with AI-powered information evaluation capabilities:

- **Flask Web App** (`src/app.py`) - Main web interface with project/task management
- **CLI Pipeline** (`src/main.py`) - Standalone tool for evaluating new information against existing projects
- **Database Models** - SQLAlchemy models for Project, Task, and Resource entities
- **AI Evaluation Pipeline** - Uses LLM providers to assess information relevance

### Core Components

#### Data Models (`src/models/`)
- **Project**: Core entity with name, description, purpose, desired_outcome, status, priority
- **Task**: Belongs to projects, has description, context, status, priority, sort_order
- **Resource**: Belongs to tasks, represents URLs/links with metadata and consumption status

#### Web Interface (`src/api/routes.py`)
- Full CRUD operations for projects, tasks, and resources
- Task reordering functionality via AJAX
- JSON export endpoints for project data (`/projects/<id>/json` and `/projects/all/json`)
- Markdown rendering support for descriptions

#### AI Pipeline (`src/pipelines/pkm/`)
- `NewProjectInfoEvaluatorPipeline`: Evaluates new information against existing project context
- Uses structured Pydantic models for LLM responses
- Configurable LLM providers via `LLMFactory`

#### Prompt Management (`src/prompts/`)
- Jinja2 template system for prompts
- Templates stored in `src/prompts/templates/`
- `PromptManager` handles template loading and rendering

### Key Dependencies
- **Flask**: Web framework
- **SQLAlchemy**: Database ORM
- **Alembic**: Database migrations
- **Pydantic**: Data validation and structured LLM responses
- **Instructor**: LLM response parsing
- **Anthropic/OpenAI**: LLM providers
- **Langfuse**: LLM observability
- **Rich**: CLI output formatting

### CSS Styling Convention
- **BEM Methodology**: Block-Element-Modifier naming convention is used throughout the project
- CSS classes follow the pattern: `block__element--modifier`
- Example: `.table__cell--highlighted`, `.button__icon--primary`

### Environment Configuration
- Database connection via `DATABASE_URL`
- Flask secret key via `FLASK_SECRET_KEY`
- LLM API keys for configured providers
- Uses python-dotenv for environment loading

### File I/O Patterns
- CLI pipeline reads from `input.txt` in project root
- Templates use Jinja2 with `.j2` extension
- Static assets served from `src/static/`
- HTML templates in `src/templates/` with subdirectories by feature