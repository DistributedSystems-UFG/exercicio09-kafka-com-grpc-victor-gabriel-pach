[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/A6uVSc3Y)


# Exercício 09 — Kafka + gRPC (Python)

Este projeto implementa um sistema distribuído que combina dois paradigmas de interação: **pub-sub** (com Apache Kafka) e **cliente-servidor** (com gRPC). O sistema simula sensores de temperatura, processa os dados e os disponibiliza para consulta via web service.

## Arquitetura

```
[sensor.py] → (Kafka: temperature-raw) → [processor.py] → (Kafka: temperature-avg) → [service.py] ↔ [client.py]
```

- **sensor.py** — simula um sensor que publica leituras de temperatura no tópico `temperature-raw` sempre que há uma variação significativa (≥ 0.5°C)
- **processor.py** — consome o tópico `temperature-raw`, calcula a média das últimas 10 leituras e publica o resultado no tópico `temperature-avg`
- **service.py** — consome o tópico `temperature-avg`, armazena os dados em memória e expõe um servidor gRPC para consulta
- **client.py** — cliente gRPC que consulta o serviço para obter a última média, o histórico completo e a média em um intervalo de tempo

## Tecnologias utilizadas

- Python 3
- Apache Kafka 3.7.0 (pub-sub)
- gRPC + Protocol Buffers (cliente-servidor)
- kafka-python
- grpcio / grpcio-tools

## Pré-requisitos

- Duas instâncias EC2 com Amazon Linux 2023 (kernel 6.1)
- Java 17 instalado na EC2-1 (necessário para o Kafka)
- Python 3 e pip instalados nas duas instâncias
- Portas 9092, 2181 e 50051 liberadas no Security Group

## Configuração

Edite o arquivo `const.py` com o IP privado da EC2-1 (servidor):

```python
KAFKA_HOST = "172.31.x.x"  # IP privado da EC2-1
GRPC_HOST  = "172.31.x.x"  # IP privado da EC2-1
GRPC_PORT  = "50051"
```

## Compilar o proto

Rode nas duas instâncias:

```bash
python3 -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. ./protos/TemperatureService.proto
```

## Como executar

### EC2-1 (servidor) — abrir 4 terminais

**Terminal 1 — Zookeeper:**
```bash
cd ~/kafka
bin/zookeeper-server-start.sh config/zookeeper.properties
```

**Terminal 2 — Kafka broker:**
```bash
cd ~/kafka
bin/kafka-server-start.sh config/server.properties
```

**Terminal 3 — Criar tópicos e iniciar o processor:**
```bash
cd ~/kafka
bin/kafka-topics.sh --create --topic temperature-raw --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --create --topic temperature-avg --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

cd ~/exercicio09-kafka-com-grpc-victor-gabriel-pach
python3 processor.py
```

**Terminal 4 — gRPC Service:**
```bash
cd ~/exercicio09-kafka-com-grpc-victor-gabriel-pach
python3 service.py
```

### EC2-2 (cliente) — abrir 2 terminais

**Terminal 1 — Sensor:**
```bash
python3 sensor.py
```

**Terminal 2 — Cliente gRPC (aguardar ~10 segundos):**
```bash
python3 client.py
```

## Endpoints gRPC disponíveis

| Endpoint | Descrição |
|---|---|
| `GetLatestAverage` | Retorna a média mais recente de temperatura |
| `GetHistory` | Retorna o histórico completo de médias armazenadas |
| `GetAverageInRange` | Retorna a média das leituras em um intervalo de tempo |

