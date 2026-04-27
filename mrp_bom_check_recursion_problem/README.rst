.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================================================
Create log records from BoMs that create recursion problems
===========================================================

::

    Use "Recursion Check" button on BoM tree view to if some BoMs create
    a recursion problem.

    Normally Odoo never allows creating BoMs that can create a recursion error,
    but this can be bypassed with some know-how. See if some logs were created
    by going to Manufacturing --> Reporting --> BoM recursion logs.

Configuration
=============
::

    No need to configure anything

Usage
=====
::

    Go to BoM tree view, select some BoM and then click on "Recursion Check" button.

Known issues / Roadmap
======================
::

    The module should not create any issues with other modules.

Credits
=======

Contributors
------------

* Timo Kekäläinen <timo.kekalainen@tawasta.fi>

Maintainer
----------

.. image:: http://tawasta.fi/templates/tawastrap/images/logo.png
   :alt: Oy Tawasta OS Technologies Ltd.
   :target: http://tawasta.fi/

This module is maintained by Oy Tawasta OS Technologies Ltd.
