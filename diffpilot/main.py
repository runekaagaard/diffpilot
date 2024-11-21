import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .core import run_diff_command, load_config

app = FastAPI(title="DiffPilot")

# Setup templates and static files
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Configuration class to hold settings
class Config:
    def __init__(self):
        self.dark_mode = os.getenv("DIFFPILOT_DARK_MODE", "off")
        self.refresh_interval = float(os.getenv("DIFFPILOT_REFRESH_INTERVAL", "2.0"))
        self.git_project_path = Path(os.getenv("DIFFPILOT_GIT_PROJECT_PATH", "."))
        self.diff_command = os.getenv("DIFFPILOT_DIFF_COMMAND", "git diff --color=never")

    @property
    def is_dark_mode(self):
        return self.dark_mode == "on"

# Create config on startup
@app.on_event("startup")
async def startup_event():
    app.state.config = Config()

@app.get("/")
async def home(request: Request):
    config = request.app.state.config
    try:
        diffs = run_diff_command(
            config.diff_command,
            config.git_project_path
        )
        # Load config to get tag styles
        yaml_config = load_config(config.git_project_path)
        tags_config = yaml_config.get('tags', {})
    except Exception as e:
        diffs = [{'filename': 'Error', 'content': str(e)}]
        tags_config = {}

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "DiffPilot",
            "dark_mode": request.app.state.config.is_dark_mode,
            "refresh_interval": request.app.state.config.refresh_interval,
            "git_project_path": request.app.state.config.git_project_path,
            "diffs": diffs,
            "tags_config": tags_config,
        }
    )
