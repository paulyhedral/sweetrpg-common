from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="sweetrpg-db",
    install_requires=["mongoengine", "marshmallow==3.14.0", "sweetrpg-model-core"],
    extras_require={},
)
