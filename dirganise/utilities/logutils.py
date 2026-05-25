import logging, colorlog

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