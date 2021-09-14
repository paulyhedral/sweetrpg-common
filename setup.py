from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="sweetrpg-common",
    install_requires=[
        "Flask >= 2.0",
    ],
    extras_require={},
)
