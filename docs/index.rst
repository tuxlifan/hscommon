=============================================
hscommon - Common code used throughout HS apps
=============================================

:Author: `Hardcoded Software <http://www.hardcoded.net>`_
:Dev website: http://hg.hardcoded.net/hscommon
:License: BSD License

Introduction
============

``hscommon`` is a collection of tools used throughout HS apps. It manage their build process, their job progress, their tests, etc.. Historically, the code contained here was in ``hsutil``, but I made a split so that code that was useful exclusively in HS apps would go in ``hscommon``.

Dependencies
============

Python 2.6 is required. `Nose <http://somethingaboutorange.com/mrl/projects/nose/>`_ is required to run the tests.

API Documentation
=================

.. toctree::
   :maxdepth: 2
   
   build
   cocoa
   currency
   job
   markable
   notify
   reg
   sqlite
