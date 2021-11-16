from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="sweetrpg-db",
    install_requires=["mongoengine", "marshmallow==3.14.1", "sweetrpg-model-core", "dnspython<3.0.0", "PyMongo[tls,srv]==3.12.1"],
    extras_require={},
)
