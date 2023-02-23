===========
 Changelog
===========

Version 0.0.7
-------------

- Integrating the User Request Framework ``openacct.contrib.urf`` for generic custom request logic
- URF integrates into the Django Admin site
- Added signal handler logic for Projects and Users to automatically create UserProjectEvent objects when memberships change
- Added additional metadata to Jobs
- Updates to the Django admin for core data model

Version 0.0.6
-------------

- Adding a ``JobEditView`` endpoint so job info can be uploaded by automated systems
- Tweaks to how project memberships are displayed on the admin site

Version 0.0.5
-------------

- Bug fixes
- Adding the ``ProjectForm`` and adding some extra logic when creating a project in the admin

Version 0.0.4
-------------

- Adding shortcut functions for recording jobs and transactions
- Adding specifiers to several fields on the Job model.

Version 0.0.3
-------------

- Adding Jobs to the web API
- Setting up the basic Django Admin for the models

Version 0.0.2
-------------

- Starting the Web API with some informational views.

Version 0.0.1
-------------

- Initial Release.


Version 0.0.0
-------------

- Pre-release build.
