.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===============================
Lightweight Product Revisioning
===============================

 * Adds a "Create New Revision" button to products that do not have BOMs org
   variants.
 * Clicking the button archives the product, creates a duplicate of it, finds
   all the BOMs the old product was a component of and replaces those products
   with the new product revision
 * Old BOMs get archived, get a "Valid Until" date of current date, and get 
   replaced with a new BOM

Configuration
=============
\-

Usage
=====
\-

Known issues / Roadmap
======================
* The module does not have variant support, and prevents revisioning attempts 
  if the product has multiple variants.

Credits
=======

Contributors
------------
* Timo Talvitie <timo.talvitie@tawasta.fi>

Maintainer
----------

.. image:: https://tawasta.fi/templates/tawastrap/images/logo.png
   :alt: Oy Tawasta OS Technologies Ltd.
   :target: https://tawasta.fi/

This module is maintained by Oy Tawasta OS Technologies Ltd.
