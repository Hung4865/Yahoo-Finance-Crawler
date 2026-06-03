import json
from confluent_kafka import Consumer
from elasticsearch import Elasticsearch
from logger import get_logger

logger = get_logger("ElasticWorker")

def main():
    logger.info("Starting Elastic Worker...")
    
    # Initialize Elasticsearch Client
    try:
        es_client = Elasticsearch(["http://localhost:9200"])
    except Exception as e:
        logger.error(f"Failed to connect to Elasticsearch: {e}")
        return
        
    # Initialize Kafka Consumer
    conf = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'elastic_consumer_group',
        'auto.offset.reset': 'earliest'
    }
    
    consumer = Consumer(conf)
    consumer.subscribe(['scraped_articles'])
    
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                logger.error(f"Consumer error: {msg.error()}")
                continue
                
            # Parse message
            try:
                article = json.loads(msg.value().decode('utf-8'))
                
                # Index into Elasticsearch
                es_client.index(index="yahoo_articles", document=article)
                logger.info(f"Indexed in Elasticsearch: {article.get('title')}")
            except Exception as e:
                logger.error(f"Failed to process message: {e}")
                
    except KeyboardInterrupt:
        logger.info("Stopping Elastic Worker...")
    finally:
        consumer.close()

if __name__ == '__main__':
    main()
