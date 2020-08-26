==========
 OpenAcct
==========

OpenAcct is a pluggable Django app for managing research computing center project accounting.

It is intended to provide a flexible, scheduler-agnostic alternative to other Allocation and Account Management Database 
tools like Gold, Moab Account Manager, and the SlurmDBD. OpenAcct allows for definition of multiple services per system, 
each with their own units of consumption and charge rates. Charging is managed through Transactions, which binds an 
Account and Service with an amount consumed. Transactions objects can then be individually recorded, selectively billed 
and refunded when needed to maintain a complete history of Account Activity.

--------------
 Installation
--------------

``django-openacct`` can be installed from PyPI, and requires no external dependencies aside from Django.

::
    
    ?> pip install django-openacct


