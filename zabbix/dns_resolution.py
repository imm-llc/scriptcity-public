import socket

def resolution_check():

    # Something on your local network
    LOCAL_RESOLUTION_HOSTNAME = ""

    # Something outside of your local network
    REMOTE_RESOLUTION_HOSTNAME = "google.com"

    STATUS = 0

    try:
        socket.gethostbyname(LOCAL_RESOLUTION_HOSTNAME)
    except:
        STATUS += 1
    try:
        socket.gethostbyname(REMOTE_RESOLUTION_HOSTNAME)
    except:
        STATUS += 1

    print(STATUS)

resolution_check()