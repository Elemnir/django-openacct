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

-------------
 Quick Start
-------------

The following shows a small setup script being piped into the Django shell interpreter::

    ?> cat openacct_example.py

    from openacct.models    import *
    from openacct.shortcuts import *

    # Create a System and Service for a cluster
    cluster = System.objects.create(name='cluster', description='A Cluster')
    service = Service.objects.create(
        name='cluster-core-hours', units='core-hours', system=cluster,
        charge_rate=0.05, description='CPU core usage * wallclock hours'
    )

    # Create Users
    bob = User.objects.create(name='bob')
    sue = User.objects.create(name='sue')
    tux = User.objects.create(name='tux')

    # Create Projects and grant access to the cluster's service
    phys = create_project('phys', pi=bob, description='Physics Dept')
    chem = create_project('chem', pi=sue, description='Chemsitry Dept')
    grant_service_access(service, project=phys)
    grant_service_access(service, project=chem)

    # Add a user to the projects
    add_user_to_project(tux, chem)
    add_user_to_project('tux', 'phys')


    ?> ./manage.py shell < openacct_example.py


This example shows a basic setup for a center, with a single compute resource 
which is charged on a per core-hour basis. Several users and two projects, one 
for a Physics Department, and another for a Chemistry Department, are created. 

Access to use a service is managed through Accounts, which are being implicitly
created for each project. When passing the ``project`` parameter to 
``grant_service_access``, all active accounts are granted the same access.
Accounts can be created explicitly and granted access individually when desired.

Finally, the user ``tux`` is added to both of the created projects, 
demonstrating how the shortcut functions will accept both the name of an object 
or the object itself for all parameters referencing one of the models in the 
schema.

With this setup in place, job records could be added to the database as Job
objects, with Transactions making use of the ``cluster-core-hour`` service 
linked to them.
