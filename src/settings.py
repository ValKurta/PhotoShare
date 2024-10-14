import logging

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d in %(funcName)s]",
    handlers=[logging.FileHandler("errors.log"), logging.StreamHandler()],
)

logger = logging.getLogger("REST-APP")  
logger.setLevel(logging.DEBUG)  

