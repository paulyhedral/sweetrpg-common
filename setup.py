from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="sweetrpg-db",
    install_requires=["mongoengine @ git+https://github.com/MongoEngine/mongoengine.git", "marshmallow==3.14.1", "sweetrpg-model-core", "dnspython<3.0.0", "PyMongo[srv]==4.0.2"],
    extras_require={},
)
