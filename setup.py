from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="sweetrpg-db",
    install_requires=[
        "marshmallow~=3.0",
        "mongoengine~=0.27",
        "sweetrpg-model-core",
        "PyMongo[srv]~=4.0",
        "dnspython~=2.0",
    ],
    extras_require={},
)
