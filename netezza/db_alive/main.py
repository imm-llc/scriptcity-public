from config import NZ_HOST, NZ_PORT

from time import sleep
from slack import slack_alert
import socket

def check_database():

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((NZ_HOST, NZ_PORT))

        sleep(1)

        s.shutdown(socket.SHUT_WR)
        s.close()

    except Exception as e:
        slack_alert(str(e))


if __name__ == "__main__":
    check_database()



