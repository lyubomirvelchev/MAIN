# Be sure to pip install polygon-api-client

import time

from polygon import WebSocketClient, STOCKS_CLUSTER


def my_custom_process_message(message):
    print("MAIKA TI PEDAL", message)


def my_custom_error_handler(ws, error):
    print("this is my custom error handler", error)


def my_custom_close_handler(ws):
    print("this is my custom close handler")


def main():
    key = 'f7VRP_aWw41goYNDJwu_yJ4EFK4NL6K7'
    my_client = WebSocketClient(STOCKS_CLUSTER, key, my_custom_process_message)
    my_client.run_async()

    my_client.subscribe("A.MSFT", "A.AAPL", "AM.MSFT", "AM.AAPL")

    time.sleep(5)

    my_client.close_connection()


if __name__ == "__main__":

    while True:
        main()
        time.sleep(1)
