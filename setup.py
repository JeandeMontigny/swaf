"""Installation script for swaf"""

from setuptools import setup

requirements = [
    "numpy",
    "scipy",
    "neo",
    "multiprocessing",
]

# Usage: pip install -e .[dev]
extra_requirements = {
    "dev": [
        "ipykernel",
        "ipython",
        "jupyterlab",
    ]
}

setup(
    author="Jean de Montigny",
    description="Spike2 Waveform Analysis Framework",
    extras_require=extra_requirements,
    install_requires=requirements,
    license="",
    name="swaf",
    packages=["swaf"],
    url="",
    version="0.1",
)
