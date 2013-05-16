#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django import forms
from django.contrib import admin
from lck.django.common.admin import ModelAdmin

from ajax_select.fields import AutoCompleteSelectField

from ralph_assets_imports.models import ImportRecord
from django.utils.html import escape
from ajax_select import LookupChannel
from ralph.discovery.models import Device
from django.db.models import Q

from ralph_assets.models import RalphDeviceLookup


class DeviceLookup(LookupChannel):
    model = Device

    def get_query(self, q, request):
        query = Q(
            Q(
                Q(barcode__istartswith=q) |
                Q(sn__istartswith=q) |
                Q(id__startswith=q) |
                Q(model__name__icontains=q)
            )
        )
        return Device.objects.filter(query).order_by('sn')[:10]

    def get_result(self, obj):
        return obj.id

    def format_match(self, obj):
        return self.format_item_display(obj)

    def format_item_display(self, obj):
        return """
        <li class='asset-container'>
            <span class='asset-model'>id:%s</span><br>
            <span class='asset-model'>sn:%s</span><br>
            <span class='asset-model'>bc:%s</span><br>
            <span class='asset-model'>name:%s</span><br>
            <span class='asset-model'>model:<b>%s</b></span><br>
        </li>
        """ % (escape(obj.id), escape(obj.sn), escape(obj.barcode or ''), escape(obj.name), escape(obj.model.name))


class ImportRecordAdminForm(forms.ModelForm):
    class Meta:
        model = ImportRecord

    device_id = AutoCompleteSelectField(
        ('ralph_assets_imports.admin', 'DeviceLookup'), required=False
    )

    def clean_device_id(self, *args, **kwargs):
        self.device_id = self.data['device_id'] or None
        return self.device_id

    def clean(self, *args, **kwargs):
        self.created_by = []
        self.modified_by = []

        return super(ImportRecordAdminForm, self).clean(*args, **kwargs)


class ImportRecordAdmin(ModelAdmin):
    form = ImportRecordAdminForm
    list_display = ('barcode', 'sn', 'device_id')
    search_fields = ('barcode', 'sn', 'device_id')

admin.site.register(ImportRecord, ImportRecordAdmin)

