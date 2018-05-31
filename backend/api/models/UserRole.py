"""
    REST API Documentation for the NRS TFRS Credit Trading Application

    The Transportation Fuels Reporting System is being designed to streamline
    compliance reporting for transportation fuel suppliers in accordance with
    the Renewable & Low Carbon Fuel Requirements Regulation.

    OpenAPI spec version: v1


    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from django.db import models

from auditable.models import Auditable

from .Permission import Permission
from .RolePermission import RolePermission


class UserRole(Auditable):
    user = models.ForeignKey('User',
                             related_name='user_roles',
                             on_delete=models.CASCADE)
    role = models.ForeignKey('Role',
                             related_name='user_roles',
                             on_delete=models.CASCADE)

    @property
    def permissions(self):
        role_permissions = RolePermission.objects.filter(role_id=self.role_id)

        return role_permissions

    class Meta:
        db_table = 'user_role'
