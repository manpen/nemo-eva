import os


def data_path():
    return os.environ.get(
        "DATA_PATH",
        os.path.dirname(os.path.realpath(__file__)) + "/../data/"
    )
