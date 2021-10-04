from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="sweetrpg-db",
    install_requires=["mongoengine", "marshmallow==3.13", "sweetrpg-model-core @ git+https://github.com/sweetrpg/model-core.git@develop"],
    extras_require={},
)
