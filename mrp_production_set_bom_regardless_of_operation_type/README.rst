.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================================
Set BoM that is not based on Operation Type
===========================================

Normally a production order's Operation Type is used to search for
a BoM for a product. So the BoM that is being search for has to
have the same Operation Type as its production order's Operation
Type or the Operation Type needs to be False (on BoM). This module
changes this and Operation Type is not used when searching for a BoM.
Then BoMs with different Operation Types than a production order's
Operation Type are also being searched for.

Configuration
=============
\-

Usage
=====
Install the module from Apps.

Known issues / Roadmap
======================
\-

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
