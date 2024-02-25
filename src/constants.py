import os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
AVAILABLE_DIR = REPO_ROOT / "available"
LOG_DIR = REPO_ROOT / "log"
CONFIG_DIR = REPO_ROOT / "config"
CONFIG_GLOBAL_SECTION = "global"
ISO_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
QUERY_TIME_FORMAT = "%Y/%m/%d %H:%M:%S.000"
IS_PRODUCTION = os.environ.get("ENVIRONMENT") == "prod"
