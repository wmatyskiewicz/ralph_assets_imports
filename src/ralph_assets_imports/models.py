#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Asset management models."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

from django.db import models
from django.utils.translation import ugettext_lazy as _
from lck.django.common.models import (
    EditorTrackable,
    Named,
    SoftDeletable,
    TimeTrackable,
    ViewableSoftDeletableManager
)
from lck.django.choices import Choices
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from uuid import uuid4

from ralph.business.models import Venture
from ralph.discovery.models_device import Device, DeviceType
from ralph.discovery.models_util import SavingUser

SAVE_PRIORITY = 0


class ImportRecord(TimeTrackable, EditorTrackable, SavingUser, SoftDeletable):
    device = models.ForeignKey(Device, null=True)

    model = models.CharField(
        verbose_name='Model urzadzenia',
        max_length=1024,
        blank=True,
    )
    device_type = models.CharField(
        verbose_name='Typ urzadzenia',
        max_length=1024,
        blank=True,
    )
    sn = models.CharField(
        verbose_name='S/N',
        max_length=128,
        blank=True,
    )
    barcode = models.CharField(
        verbose_name='Barcode',
        max_length=128,
        blank=True,
    )
    rack = models.CharField(
        verbose_name='Szafa',
        max_length=128,
        blank=True,
    )
    u_level = models.CharField(
        verbose_name='Poziom U',
        max_length=128,
        blank=True,
    )
    u_height = models.CharField(
        verbose_name='Wysokosc urzadzenia',
        max_length=128,
        blank=True,
    )
    dc = models.CharField(
        verbose_name='Data Center',
        max_length=128,
        blank=True,
    )
    info = models.CharField(
        verbose_name='Uwagi',
        max_length=128,
        blank=True,
    )
    niw = models.CharField(
        verbose_name='NIW',
        max_length=128,
        blank=True,
    )
    fv = models.CharField(
        verbose_name='Nr faktury',
        max_length=128,
        blank=True,
    )
    name = models.CharField(
        verbose_name='Nazwa',
        max_length=128,
        blank=True,
    )
    invent_value = models.CharField(
        verbose_name='Wartosc inwentarzowa',
        max_length=128,
        blank=True,
    )
    date = models.CharField(
        verbose_name='Data przyjecia',
        max_length=128,
        blank=True,
    )
    price_netto = models.CharField(
        verbose_name='Cena netto',
        max_length=128,
        blank=True,
    )
    deprecation_rate = models.CharField(
        verbose_name='Stopa amortyzacji',
        max_length=128,
        blank=True,
    )
    imported = models.BooleanField(
        default=False,
    )
    second_sn = models.CharField(
        verbose_name='Drugi SN',
        max_length=128,
        blank=True,
    )
    errors = models.CharField(
        max_length=2048,
        blank=True,
        null=True,
    )

    def __unicode__(self):
        return "%s (%s, bc:%s)" % (self.model, self.sn, self.barcode)

