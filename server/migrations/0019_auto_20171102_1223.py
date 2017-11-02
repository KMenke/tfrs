# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-02 19:23
from __future__ import unicode_literals

from django.db import migrations, models
from django.db.models import F


class Migration(migrations.Migration):
    dependencies = [
        ('server', '0018_auto_20171016_1514'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='credittradehistory',
            options={'ordering': ['-create_timestamp']},
        ),
        migrations.AddField(
            model_name='credittrade',
            name='fairMarketValuePerCreditDecimal',
            field=models.DecimalField(decimal_places=2, default=None,
                                      max_digits=999, null=True),
        ),
        migrations.AddField(
            model_name='credittradehistory',
            name='newFairMarketValuePerCreditDecimal',
            field=models.DecimalField(decimal_places=2, default=None,
                                      max_digits=999, null=True),
        ),
        migrations.RunSQL(
            'UPDATE credit_trade SET '
            '"fairMarketValuePerCreditDecimal" = '
            'CAST( CASE WHEN "fairMarketValuePerCredit" = \'\''
            '           THEN \'0\''
            '           ELSE "fairMarketValuePerCredit"'
            '           END AS numeric(10,2) '
            ');')
    ]

