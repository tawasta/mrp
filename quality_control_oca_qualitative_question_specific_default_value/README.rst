.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================================================================
Quality Control OCA: Specific Default Value for Qualitative Questions
=====================================================================

* Adds a "Default pre-fill value" checkbox column to the answers list
  of qualitative test questions.
* Lets you define, per question, which correct answer should be used
  to pre-fill the answer when the test's "Pre-fill with correct
  values" option is enabled, instead of always using the first
  correct answer found.

Configuration
=============
* None needed

Usage
=====
* When defining a qualitative test question, optionally tick
  "Default pre-fill value" on one of its correct answers.
* Only correct answers can be flagged, and only one answer per
  question can be flagged at a time.
* If no answer is flagged, pre-fill continues to use the first
  correct answer found, as before this module was installed.

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
