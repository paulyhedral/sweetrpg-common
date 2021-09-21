from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="sweetrpg-db",
    install_requires=["Flask-PyMODM @ https://github.com/sweetrpg/flask-pymodm.git"],
    extras_require={},
)
