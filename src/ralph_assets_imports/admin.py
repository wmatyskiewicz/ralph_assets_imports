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
            <span class='asset-model'>%s</span>
            <span class='asset-barcode'>%s</span>
            <span class='asset-sn'>%s</span>
        </li>
        """ % (escape(obj.model), escape(obj.barcode or ''), escape(obj.sn))


class ImportRecordAdminForm(forms.ModelForm):
    class Meta:
        model = ImportRecord

    device = AutoCompleteSelectField(
        ('ralph_assets.models', 'RalphDeviceLookup')
    )


class ImportRecordAdmin(ModelAdmin):
    form = ImportRecordAdminForm
    #list_display = ('ci', 'path', 'is_regex')
    #search_fields = ('ci', 'is_regex', 'path',)
    #save_on_top = True

admin.site.register(ImportRecord, ImportRecordAdmin)

