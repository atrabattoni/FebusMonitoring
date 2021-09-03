from setuptools import setup

setup(
    name="febus",
    packages=["febus"],
    entry_points={
        "console_scripts": [
            "FebusMonitor = febus.main:main",
        ],
    },
)
