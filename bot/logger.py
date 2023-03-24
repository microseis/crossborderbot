import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.basicConfig(
    filename="app.log",
    filemode="w",
    format="%(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
