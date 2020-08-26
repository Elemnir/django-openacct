==========
 OpenAcct
==========

OpenAcct is a pluggable Django app for managing research computing center project accounting.

It is intended to provide a flexible, scheduler-agnostic alternative to other Allocation and Account Management Database 
tools like Gold, Moab Account Manager, and the SlurmDBD. OpenAcct allows for definition of multiple Services per System, 
each with their own units of resource consumption and charge rates. Charging is managed through Transactions, which bind 
an amount of a Service's resources consumed with an Account responsible for any charges incurred by that consumption. 
Transaction objects can be individually tracked, selectively charged, and refunded when needed to maintain an event-based 
history of account activity.

--------------
 Installation
--------------

``django-openacct`` can be installed from PyPI, and requires no external dependencies aside from Django.

::
    
    ?> pip install django-openacct


