.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================================================
MRP Subcontracting: Process computations as sudo
================================================

Process computations as sudo when using MRP Subcontracting.

This module is meant to be extended if other MRP Subcontracting related
computations are needed to be processed as an admin user (sudo). The module
was created to bypass company related restrictions and mainly now (9.6.2025)
it bypasses those restrictions when returing pickings.

Configuration
=============
None are needed at the moment

Usage
=====
A user only needs to install this module

Known issues / Roadmap
======================
A user gains access to locations which he/she previously did not have
an access to. But this should not be a problem, because those locations
are subcontracting locations.

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
