# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This is the models directory for the iris project.

Models for the whole project go here, unless they
belong to one and only one application specifically.

This is to avoid interop issues between applications for this project.

When adding a model, please revise the following scheme.

Added models should go under __all__ member of this __init__ file
to be importable by Django for database operations.
"""

# __all__ contains the modules that are available from this folder.
# Extend __all__ with the models you want to expose from iris.core.models.
__all__ = []

# Package Database related model imports:
from iris.core.models.packagedb import (Domain, SubDomain, License,
    GitTree, Package, Product, Image, role_users)
from iris.core.models.submissions import (
    PackageBuild, ImageBuild, Submission, SubmissionBuild, BuildGroup,
    SubmissionGroup, Snapshot, DISPLAY_STATUS)
from iris.core.models.user import (UserProfile, UserParty,
    DomainRole, SubDomainRole, GitTreeRole)


__all__.extend(['Domain', 'SubDomain', 'License', 'GitTree', 'Package',
                'Product', 'Image', 'role_users'])
__all__.extend(['PackageBuild', 'ImageBuild', 'Submission', 'SubmissionBuild',
                'BuildGroup', 'SubmissionGroup', 'Snapshot', 'DISPLAY_STATUS'])
__all__.extend(['UserProfile', 'UserParty',
                'DomainRole', 'SubDomainRole', 'GitTreeRole', ])
