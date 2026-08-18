.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================================================================
Quality Control OCA: Specific Default Value for Quantitative Questions
======================================================================

* Adds a "Use specific pre-fill value" toggle and a "Default value"
  field to quantitative test questions.
* Lets you define, per question, the exact value that should be used
  to pre-fill the answer when the test's "Pre-fill with correct
  values" option is enabled, instead of always using the midpoint of
  Min/Max.

Configuration
=============
* None needed

Usage
=====
* When defining a quantitative test question, optionally enable "Use
  specific pre-fill value" and set the "Default value" that appears.
* If "Use specific pre-fill value" is left disabled, pre-fill
  continues to use the midpoint of Min/Max, as before this module was
  installed.
* If enabled, the configured "Default value" is used to
  pre-fill the answer instead.

Known issues / Roadmap
======================
\-

Credits
=======

Contributors
------------

* Timo Talvitie <timo.talvitie@futural.fi>

Maintainer
----------

.. image:: https://futural.fi/templates/tawastrap/images/logo.png
        :alt: Futural Oy
        :target: https://futural.fi/

This module is maintained by Futural Oy
