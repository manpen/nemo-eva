import os

data_path = os.environ.get(
    "DATA_PATH",
    os.path.dirname(os.path.realpath(__file__)) + "/../data/"
)
