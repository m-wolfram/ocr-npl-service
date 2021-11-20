import os
import socket


def check_docker_environment():
    """Function checks if project run in a project docker environment."""

    docker_flag = os.environ.get('DOCKER_FLAG', False)

    return docker_flag


def get_ip():
    """Function gets host machine ip address.
    It is used in docker environment setup.
    WARNING: It's not a 100% solution.
    Ip address can be incorrect, but works inside docker."""

    try:
        ip = socket.gethostbyname(socket.gethostname() + ".local")
    except:
        ip = socket.gethostbyname(socket.gethostname())

    return ip
