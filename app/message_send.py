import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='reg_form')

channel.basic_publish(exchange='', routing_key='reg_form', body='18')
connection.close()
