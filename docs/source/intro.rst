.. _intro:

Introduction to PiedPiper
=========================

PiedPiper is a managed Pipeline validation and execution framework. 

The problem Piedpiper is trying to solve is two-fold.

1. How does a developer ensure their change will be accepted by the CI framework
   without making a commit?

2. How can a managerial entity enforce specific pipeline steps and configurations
   for each project that they oversee? 

PiedPiper was created to help solve these two problems. The intention is to give developers
the ability to quickly bootstrap a project with a set of pipeline configurations that will
run through the full pipeline. Piedpiper is the framework which will help achieve these two
stated goals.

The ``picli`` is the entrypoint to PiedPiper. This is the commandline client used by developers
and CI platforms which will provide a standard interface into the CI/CD system. ``picli`` was
created to ensure that developers could test their changes before making commits to a repository
and be fairly confident that a change would make its way through the CI system. Additionally, ``picli``
allows for a set of validations to be applied to the CI platform configuration which can be 
used to enforce specific settings and/or steps.

.. note::
    To find more information on the architecture of PiedPiper see the :ref:`Architecture Guide<architecture>`.


