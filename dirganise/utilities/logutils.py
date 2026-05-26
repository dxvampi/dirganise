import logging, colorlog
from pathlib import Path
from platformdirs import user_cache_dir

def config_logs() -> logging.Logger:
    handler = colorlog.StreamHandler()

    formatter = colorlog.ColoredFormatter(
        "%(log_color)s[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        }
    )
    handler.setFormatter(formatter)

    logger = colorlog.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    return logger

def get_undo_log_path(undo_file_name: str) -> Path:
    log_dir = Path(user_cache_dir(appname="dirganise", appauthor="dxvampi"))
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / undo_file_name