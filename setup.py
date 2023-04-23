import sys

sys.stderr.write(
    "This setup.py is not meant to be used. Please use pip to install this package."
)
sys.exit()

from setuptools import setup  # noqa: E402

setup(
    name="qt-command-palette",
    install_requires=[
        "qtpy>=2.0.0",
    ],
)
