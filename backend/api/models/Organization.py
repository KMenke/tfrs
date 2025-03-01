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
from datetime import date
from django.db import models
from django.db.models import F

from api.managers.OrganizationManager import OrganizationManager
from auditable.models import Auditable
from .OrganizationAddress import OrganizationAddress
from .OrganizationBalance import OrganizationBalance


class Organization(Auditable):
    """
    Contains a list of all of the recognized Part 3 fuel suppliers, both
    past and present, as well as an entry for the government which is also
    considered an organization.
    """
    name = models.CharField(
        max_length=500,
        db_comment="Organization's legal name"
    )
    status = models.ForeignKey(
        'OrganizationStatus',
        related_name='organizations',
        on_delete=models.PROTECT
    )
    actions_type = models.ForeignKey(
        'OrganizationActionsType',
        related_name='organizations',
        on_delete=models.PROTECT
    )
    type = models.ForeignKey(
        'OrganizationType',
        related_name='organizations',
        blank=True, null=True,
        on_delete=models.PROTECT
    )
    objects = OrganizationManager()

    def __str__(self):
        return self.name

    @property
    def actions_type_display(self):
        return self.actions_type.the_type

    @property
    def organization_address(self):
        """
        Gets the active address for the organization
        """
        data = OrganizationAddress.objects.filter(
            effective_date__lte=date.today(),
            organization_id=self.id
        ).exclude(
            expiration_date__lt=date.today()
        ).exclude(
            expiration_date=F('effective_date')
        ).order_by('-effective_date', '-update_timestamp').first()

        return data

    @property
    def organization_balance(self):
        data = {
            'credit_trade_id': None,
            'validated_credits': 0
        }

        organization_balance = OrganizationBalance.objects.filter(
            organization_id=self.id,
            expiration_date=None).first()

        if organization_balance:
            data['credit_trade_id'] = organization_balance.credit_trade_id
            data['validated_credits'] = organization_balance.validated_credits

        return data

    @property
    def status_display(self):
        return self.status.status

    class Meta:
        db_table = 'organization'

    db_table_comment = "Contains a list of all of the recognized Part 3 " \
                       "fuel suppliers, both past and present, as well as " \
                       "an entry for the government which is also " \
                       "considered an organization."
