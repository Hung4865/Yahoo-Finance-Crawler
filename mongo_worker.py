import json
from confluent_kafka import Consumer
from pymongo import MongoClient
from logger import get_logger

logger = get_logger("MongoWorker")

def main():
    logger.info("Starting Mongo Worker...")
    
    # Initialize MongoDB Client
    client = MongoClient("mongodb://localhost:27017/")
    db = client.YahooFinanceDB
    articles_collection = db.Articles
    
    # Initialize Kafka Consumer
    conf = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'mongo_consumer_group',
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
                
                # Check if exists and insert
                if articles_collection.find_one({"title": article.get("title")}) is None:
                    articles_collection.insert_one(article)
                    logger.info(f"Saved to MongoDB: {article.get('title')}")
            except Exception as e:
                logger.error(f"Failed to process message: {e}")
                
    except KeyboardInterrupt:
        logger.info("Stopping Mongo Worker...")
    finally:
        consumer.close()

if __name__ == '__main__':
    main()
