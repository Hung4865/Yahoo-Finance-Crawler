import logging
import logstash

def get_logger(name):
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Standard console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Logstash UDP handler
        # Connects to the Logstash container on port 5000
        try:
            logstash_handler = logstash.LogstashHandler('localhost', 5000, version=1)
            logstash_handler.setLevel(logging.INFO)
            logger.addHandler(logstash_handler)
        except Exception as e:
            print(f"Failed to initialize Logstash handler: {e}")

    return logger
