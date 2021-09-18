from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="sweetrpg-common",
    install_requires=["marshmallow==3.13.0", "PyMongo[srv,tls]==3.12.0"],
    extras_require={},
)
