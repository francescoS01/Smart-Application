from confluent_kafka import Consumer, KafkaException, KafkaError
import json
from streaming_main import *

# Funzione che processa i dati ricevuti
def process_data(data):
    # Qui inizia la tua pipeline di processing
    print(f"Processing data: {data}")
    # Inserisci qui il codice per avviare la pipeline di processing

# Impostazioni del consumer Kafka
def create_consumer():
    consumer = Consumer({
        'bootstrap.servers': 'localhost:9092',  # Indirizzo del tuo server Kafka
        'group.id': 'my-consumer-group',  # Gruppo di consumatori (importante per il bilanciamento del carico)
        'auto.offset.reset': 'earliest'  # Se non ci sono offset memorizzati, inizia dal primo messaggio
    })
    return consumer

def consume_data():
    consumer = create_consumer()
    topic = 'my-topic'  # Nome del topic Kafka su cui stai ascoltando
    consumer.subscribe([topic])

    try:
        while True:
            msg = consumer.poll(timeout=1.0)  # Timeout di 1 secondo per la lettura del messaggio
            if msg is None:
                # Nessun messaggio disponibile, continua a cercare
                continue
            elif msg.error():
                # Se c'è un errore nel messaggio
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # Si è arrivati alla fine della partizione
                    print(f"End of partition {msg.partition} reached")
                else:
                    raise KafkaException(msg.error())
            else:
                # Il messaggio è valido, processa il dato
                data = json.loads(msg.value().decode('utf-8'))  # Decodifica il messaggio da JSON
                process_data(data)  # Avvia la pipeline di processing
    except KeyboardInterrupt:
        print("Interrotto da utente.")
    finally:
        # Assicurati di chiudere il consumer correttamente
        consumer.close()

if __name__ == '__main__':
    consume_data()

