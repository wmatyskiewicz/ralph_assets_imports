# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import Counter

from bob.data_table import DataTableColumn, DataTableMixin
from bob.menu import MenuItem, MenuHeader
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.urlresolvers import resolve, reverse
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.forms.models import modelformset_factory, formset_factory
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from ralph_assets.models import (
    Asset,
    AssetModel,
    AssetCategory,
    AssetSource,
    DeviceInfo,
    OfficeInfo,
    PartInfo,
)
from ralph_assets.models_assets import AssetType
from ralph_assets.models_history import AssetHistoryChange
from ralph.discovery.models import Device
from ralph.ui.views.common import Base
from ralph.util.api_assets import get_device_components
from ralph_assets.views import DataCenterMixin
import csv, codecs
from ralph.discovery.models import Device, DeviceType, GenericComponent
from django import forms

from ralph_assets.models import ImportRecord

class DataCenterImportAssets(DataCenterMixin):
    template_name = 'assets/import.html'
    sidebar_selected = ''

    def get(self, *args, **kwargs):
        self.form = UploadFileForm(self.request.POST, self.request.FILES)
        return super(DataCenterImportAssets, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.form = UploadFileForm(self.request.POST, self.request.FILES)
        if self.form.is_valid():
            opened_file = self.form.files['file']
            self.import_(opened_file)
            errors = self.validate(opened_file)
            self.errors = errors
        return self.get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ret = super(DataCenterImportAssets, self).get_context_data(**kwargs)
        ret.update({
            'form': self.form,
            'errors': getattr(self, 'errors', []),
        })
        return ret

    def import_(self, file_object):
        file_object.seek(0)
        reader = unicode_csv_reader(file_object, delimiter=b',', quotechar=b'"')
        for line in reader:
            lp, model, device_type, sn, barcode, box, u_level, device_height, dc, info, niw, fv, name,invent_value,date, price_netto, deprecation_rate, monthly, additional_comments, _, date_of_get = line
            i = ImportRecord(
               model=model,
               device_type=device_type,
               sn=sn,
               barcode=barcode,
               invent_value=invent_value,
               box=box,
               u_level=u_level,
               device_height=device_height,
               dc=dc,
               info=info,
               niw=niw,
               fv=fv,
               name=name,
               date=date,
               price_netto=price_netto,
               deprecation_rate=deprecation_rate,
            )
            i.save()

    def validate(self):
        import copy
        virtual = {
            DeviceType.virtual_server,
            DeviceType.cloud_server,
            DeviceType.mogilefs_storage,
        }

        data = Device.objects.exclude(
            model__type__in=virtual).values_list(
                'id', 'name', 'venture', 'venture__symbol',
                'barcode', 'sn', 'model__name'
            )

        barcodes = dict([(row[4], row[0]) for row in data])
        sns = dict([((row[5] or '').lower(), row[0]) for row in data])

        data_components = GenericComponent.objects.values_list('id', 'sn')

        components_sns = dict([(row[1].lower(), row[0]) for row in data_components])
        barcodes_copy = copy.copy(barcodes)
        sns_copy = copy.copy(sns)
        # after copy
        errors = []
        objects = ImportRecord.objects.all()
        #errors.append(['typ bledu', 'inwent lp', 'barcode', 'sn', 'model', 'ralph link'])
        for line in objects:
            lp, model, typ, sn, barcode, szafa, poziom, wysokosc, dc, uwagi, nwi, fv, nazwa, wartosc_inv,data_przyjecia, wartosc_netto, stawka_amortyzacji, miesiecznie, uwagi, _, data_przyjecia =
            sn = sn or ''
            sn = sn.lower()
            if not sn and not barcode:
                errors.append(['Brak sn oraz barcode', lp, barcode, sn, model,'',typ])
                continue

            if not barcode in barcodes:
                if not sn in sns:
                    if not sn in components_sns:
                        errors.append(['Brak w Ralph', lp, barcode, sn, model, '', typ])
                else:
                    try:
                        del sns_copy[sn]
                    except KeyError:
                        errors.append(['Duplikat w Inwent.', lp, barcode, sn, model,'',typ])
                        continue
            else:
                try:
                    del barcodes_copy[barcode]
                except KeyError:
                    errors.append(['Duplikat w Inwent.', lp, barcode, sn, model, '', typ])
                if sn:
                    try:
                        del sns_copy[sn]
                    except KeyError:
                        pass

        remaining = set(barcodes_copy.values()).union(set(sns_copy.values()))
        for row in data.filter(id__in=remaining):
            #'id', 'name', 'venture', 'venture__symbol', 'barcode', 'sn')
            errors.append(['Brak w Inwent.', '', row[4] or '', row[5] or '', row[6] or '', 'http://ralph.office/ui/search/info/%s?' % row[0],''])
        return errors


class UploadFileForm(forms.Form):
    file = forms.FileField()


def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    count = 0
    for row in csv_reader:
        count += 1
        if count == 3:
            break
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]

