from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="sweetrpg-db",
    install_requires=[
        "marshmallow<4.0",
        "mongoengine==0.26.0",
        "sweetrpg-model-core",
        "PyMongo[srv]<5.0",
        "dnspython<3.0",
    ],
    extras_require={},
)
