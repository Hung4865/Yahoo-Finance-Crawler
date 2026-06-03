# Scalable Web Crawler & Scraper for Yahoo Finance

A highly scalable, decoupled, microservices-style Python web crawler optimized for scraping articles and metadata. The project leverages **Apache Kafka** to handle ingestion pipelines, **MongoDB** for persistence, and the **ELK Stack (Elasticsearch, Logstash, Kibana)** for system logging and full-text search indexing. 

---

## System Architecture

The project has been refactored from a synchronous monolithic script into a distributed, event-driven architecture to maximize throughput and ensure high reliability.

```mermaid
flowchart TD
    %% Define Styles
    classDef python fill:#306998,stroke:#FFE873,stroke-width:2px,color:white;
    classDef docker fill:#2496ED,stroke:#0db7ed,stroke-width:2px,color:white;
    classDef db fill:#4DB33D,stroke:#3F912E,stroke-width:2px,color:white;
    classDef kafka fill:#E82D24,stroke:#C62118,stroke-width:2px,color:white;
    classDef elastic fill:#005571,stroke:#00A8E1,stroke-width:2px,color:white;
    classDef target fill:#7B1FA2,stroke:#4A148C,stroke-width:2px,color:white;

    %% Nodes
    Website([Yahoo Finance Websites]) ::: target
    
    subgraph Local Environment [Local Python Environment (Outside Docker)]
        Crawler(Crawler / Scraper) ::: python
        MongoWorker(Mongo Worker) ::: python
        ElasticWorker(Elastic Worker) ::: python
    end

    subgraph Docker Ecosystem [Docker Network]
        subgraph Messaging [Message Broker]
            Zookeeper(Zookeeper) ::: kafka
            Kafka[(Apache Kafka\nTopic: scraped_articles)] ::: kafka
        end

        subgraph ELK Stack [ELK Stack]
            Logstash(Logstash\nUDP 5000) ::: elastic
            Elasticsearch[(Elasticsearch)] ::: elastic
            Kibana([Kibana\nDashboard]) ::: elastic
        end

        MongoDB[(MongoDB)] ::: db
    end

    %% Flow/Connections
    Website -- "Selenium / Requests" --> Crawler
    
    Crawler -- "System Logs" --> Logstash
    Logstash -- "Store Logs" --> Elasticsearch
    
    Crawler == "Publish (Producer)" ==> Kafka
    Zookeeper -. "Manage State" .- Kafka
    
    Kafka == "Consume" ==> MongoWorker
    Kafka == "Consume" ==> ElasticWorker
    
    MongoWorker -- "Insert Data" --> MongoDB
    ElasticWorker -- "Index Data" --> Elasticsearch
    
    Kibana -- "Query Data & Logs" --> Elasticsearch
```

### Component Details
*   **Crawler / Scraper (Producer)**: Crawls sites, parses URLs, respects `robots.txt`, and uses Selenium to handle dynamically rendered content. Reuses Selenium WebDriver instances to avoid performance degradation. Scraped articles are published immediately to a Kafka topic.
*   **Apache Kafka**: Serves as the central messaging backbone. It decouples the speed of the crawler (fast network actions) from the databases (slower write I/O).
*   **MongoDB Worker (Consumer)**: Listens to the Kafka queue and persists raw articles into MongoDB.
*   **Elastic Worker (Consumer)**: Listens to the Kafka queue and indexes articles into Elasticsearch for instant full-text search capabilities.
*   **ELK Stack**: 
    *   **Logstash**: Collects system logs via UDP from the Crawler.
    *   **Elasticsearch**: Stores both log data and crawled articles.
    *   **Kibana**: Offers real-time dashboards to monitor crawler health, logs, and query indexed articles.

---

## Features

1.  **High-Performance Scraping**:
    *   Optimized crawler queue utilizing Python's `collections.deque` (O(1) operations).
    *   Shared, lazy-initialized Selenium WebDriver to eliminate bootstrap overhead.
2.  **Robots.txt Compliance**: Automatically reads, caches, and respects target site crawl rules.
3.  **Event-Driven Pipeline**: Decoupled ingestion ensures that database downtime or bottlenecks do not stop or slow down the crawler.
4.  **Centralized Logging**: Seamlessly ships Python application logs to Logstash using a UDP handler.
5.  **Full-Text Search & Analytics**: Query scraped articles dynamically using Kibana dashboards.

---

## Getting Started

### Prerequisites
*   Python 3.8+
*   Docker & Docker Compose
*   Google Chrome (or Firefox) and the corresponding WebDriver (e.g., ChromeDriver) installed and in your system PATH.

### 1. Installation & Environment Setup

1.  Clone the repository:
    ```bash
    git clone https://github.com/amndzdzdz/Web-Crawler.git
    cd Web-Crawler
    ```

2.  Install python dependencies locally:
    ```bash
    pip install -r requirements.txt
    ```

### 2. Launch Infrastructure (Docker)

Start MongoDB, Kafka, Zookeeper, and the ELK Stack in the background:
```bash
docker-compose up -d
```

Verify that all services are healthy and running:
```bash
docker-compose ps
```

### 3. Run the Workers (Kafka Consumers)

In separate terminal sessions or background processes, start the consumers to handle database inserts:

*   **MongoDB Worker**:
    ```bash
    python mongo_worker.py
    ```
*   **Elasticsearch Worker**:
    ```bash
    python elastic_worker.py
    ```

### 4. Run the Crawler

Start the main web crawler:
```bash
python crawler.py
```

---

## Monitoring and Search

*   **Kibana UI**: Open [http://localhost:5601](http://localhost:5601) in your browser.
    *   Navigate to **Stack Management** > **Data Views** to create data views for logs (`logstash-*`) or scraped data (`scraped-articles-*`).
    *   Use the **Discover** tab to search and analyze logs and articles in real time.
*   **MongoDB**: Access your database at `mongodb://localhost:27017` using MongoDB Compass or other shell utilities.
