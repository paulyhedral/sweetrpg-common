.. _api:

Library
=======

.. module:: sweetrpg_db

This part of the documentation covers all the public API for the SweetRPG
DB library. These are common functions and classes that other SweetRPG
packages make use of.


Utilities
---------

Utility functions that may be useful anywhere.

.. autofunction:: sweetrpg_db.utils.to_datetime
.. autofunction:: sweetrpg_db.utils.to_timestamp

Database Classes
----------------

Classes used for database model and schema objects.

.. autoclass:: sweetrpg_db.schema.base.BaseDBSchema
   :members:
   :undoc-members:
   :private-members:

.. autoclass:: sweetrpg_db.exceptions.ObjectNotFound

MongoDB Repository
------------------

.. autoclass:: sweetrpg_db.mongodb.options.QueryOptions
   :members:
   :undoc-members:
   :private-members:

.. autoclass:: sweetrpg_db.mongodb.repo.MongoDataRepository
   :members:
   :undoc-members:
   :private-members:
