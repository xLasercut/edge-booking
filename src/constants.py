from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
LOG_DIR = REPO_ROOT / "log"
CONFIG_DIR = REPO_ROOT / "config"
SCREENSHOT_DIR = REPO_ROOT / "screenshots"
CONFIG_GLOBAL_SECTION = "global"
ISO_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
QUERY_TIME_FORMAT = "%Y/%m/%d %H:%M:%S.000"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"


class Drivers:
    LOCAL = "local"
    REMOTE = "remote"
