# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ralph_assets.models import (
    Asset,
    AssetModel,
    AssetCategory,
    AssetSource,
    DeviceInfo,
    OfficeInfo,
    PartInfo,
)

from ralph_assets.views import DataCenterMixin
from ralph.discovery.models import Device, DeviceType, GenericComponent
from django import forms

from ralph_assets_imports.models import ImportRecord
from ralph.util.views import csvify
import csv
import decimal
from django.http import HttpResponseRedirect
from ralph_assets.models import Asset, DeviceInfo, PartInfo, AssetType,AssetCategoryType, Warehouse, AssetSource
from django.db import transaction
import logging


class DataCenterImportAssets(DataCenterMixin):
    template_name = 'assets/import.html'
    sidebar_selected = ''

    @csvify
    def get_csv(self, *args, **kwargs):
        record_fields = ['model', 'device_type', 'sn', 'barcode',
            'invent_value', 'rack', 'u_level', 'u_height',
            'dc', 'info', 'niw', 'fv', 'name', 'date',
            'price_netto', 'deprecation_rate', 'second_sn']

        ralph_fields = ['id', 'name', 'venture', 'barcode', 'sn']

        for i in self.validate():
            if i[0] == 'error_ralph':
                yield [','.join(i[2])] + [unicode(getattr(i[1], field)) for field in record_fields]
            elif i[0] == 'error_inwent':
                yield ['Brak w inwentaryzacji'] + [unicode(i[1][field]) for field in ralph_fields]

    def create_asset(self, record_id):
        obj = ImportRecord.objects.get(id=record_id)
        ass = Asset.create(
            base_args=dict(
                type=AssetType.data_center,
                model=AssetModel.concurrent_get_or_create(name=obj.model)[0],
                category=AssetCategory.concurrent_get_or_create(
                    name=obj.device_type,defaults=dict(type=AssetCategoryType.data_center))[0],
                invoice_no=obj.fv,
                price=decimal.Decimal(str(obj.invent_value.replace(',', '.')) or 0),
                remarks=obj.info + '\n' + 'Inw. name: ' + obj.name,
                niw=obj.niw,
                production_use_date=obj.date,
                source=AssetSource.shipment,
                sn=obj.sn,
                barcode=obj.barcode,
                deprecation_rate=decimal.Decimal(obj.deprecation_rate.replace(',','.') or 0),
                warehouse=Warehouse.concurrent_get_or_create(name=obj.dc)[0],
            ),
            device_info_args=dict(
                ralph_device=obj.device,
                u_level=obj.u_level,
                u_height=obj.u_height,
                size=0,
                rack=obj.rack,
            ),
        )
        ass.save()

    def get(self, *args, **kwargs):
        if self.request.GET.get('csv'):
            return self.get_csv(*args, **kwargs)
        create_id = self.request.GET.get('create_id', '')
        if create_id:
            self.create_asset(create_id)
            return HttpResponseRedirect("/")

        self.form = UploadFileForm(self.request.POST, self.request.FILES)
        self.import_errors = dict();
        self.import_errors['ralph'] = [];
        self.import_errors['inwent'] = [];
        for i in self.validate():
            if i[0] == 'error_ralph':
                self.import_errors['ralph'].append(i)
            elif i[0] == 'error_inwent':
                self.import_errors['inwent'].append(i)
        return super(DataCenterImportAssets, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.form = UploadFileForm(self.request.POST, self.request.FILES)
        if self.form.is_valid():
            opened_file = self.form.files['file']
            ImportRecord.objects.all().delete()
            Asset.admin_objects.all().delete()
            AssetModel.objects.all().delete()
            AssetCategory.objects.all().delete()
            Warehouse.objects.all().delete()
            DeviceInfo.admin_objects.all().delete()
            OfficeInfo.admin_objects.all().delete()
            PartInfo.admin_objects.all().delete()
            self.import_(opened_file)
            for i in self.validate():
                if i[0] == 'ok':
                    try:
                        with transaction.commit_on_success():
                            ir = ImportRecord.objects.get(id=i[1].id)
                            ir.device = i[2]['paired']
                            ir.save()
                            self.create_asset(i[1].id)
                            ir.imported = True
                            ir.save()
                    except Exception as e:
                        #transaction.rollback()
                        ir = ImportRecord.objects.get(id=i[1].id)
                        ir.errors = str(e)
                        ir.imported = False
                        ir.save()
                        logging.error('error importing', exc_info=e)

        return self.get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ret = super(DataCenterImportAssets, self).get_context_data(**kwargs)
        ret.update({
            'form': self.form,
            'import_errors': self.import_errors,
        })
        return ret

    def import_(self, file_object):
        file_object.seek(0)
        reader = unicode_csv_reader(
            file_object, delimiter=b',', quotechar=b'"')
        for line in reader:
            subset = line[0:20]
            subset = [self.cleaner(field) for field in subset]
            (lp, model, device_type, sn, barcode, rack, u_level, u_height,
            dc, info, niw, fv, name,invent_value,date, price_netto,
            deprecation_rate, monthly, account_comments,second_sn) = subset
            i = ImportRecord(
               model=model,
               device_type=device_type,
               sn=sn,
               barcode=barcode,
               invent_value=invent_value,
               rack=rack,
               u_level=u_level,
               u_height=u_height,
               dc=dc,
               info=info,
               niw=niw,
               fv=fv,
               name=name,
               date=date,
               price_netto=price_netto,
               deprecation_rate=deprecation_rate,
               second_sn=second_sn,
            )
            i.save()

    def cleaner(self, s):
        s = s or ''
        s = s.replace('brak', '')
        s = s.replace('nieczytelny', '')
        s = s.strip()
        return s

    def validate(self, record_id=None):
        import copy
        virtual = {
            DeviceType.virtual_server,
            DeviceType.cloud_server,
            DeviceType.mogilefs_storage,
        }

        data = Device.objects.exclude(
            model__type__in=virtual).values(
                'id', 'name', 'venture', 'venture__symbol',
                'barcode', 'sn', 'model__name'
            )

        barcodes = dict([(self.cleaner(row['barcode']).lower(), row['id']) for row in data])
        sns = dict([((self.cleaner(row['sn'])).lower(), row['id']) for row in data])

        del sns['']; del barcodes[''];

        data_components = GenericComponent.objects.values('id', 'sn')

        components_sns = dict(
            [(self.cleaner(row['sn']).lower(), row['id']) for row in data_components])
        barcodes_copy = copy.copy(barcodes)
        sns_copy = copy.copy(sns)
        # after copy
        errors = []
        if record_id:
            objects = ImportRecord.objects.filter(id__in=[record_id], imported=False)
        else:
            objects = ImportRecord.objects.filter(imported=False)

        for record in objects:
            paired_data = {}
            errors = []
            sn = self.cleaner(record.sn).lower()
            barcode = self.cleaner(record.barcode).lower()

            #if not record.fv:
            #    errors.append('Brak fv')
            #if not record.invent_value:
            #    errors.append('Brak wart. inw.')
            #if not record.deprecation_rate:
            #    errors.append('Brak stopy amortyzacji')

            if not sn and not barcode:
                errors.append('Brak sn oraz barcode')
            if sn or barcode:
                logger.debug('has sn or barcode');
                if not barcode in barcodes:
                    logger.debug('barcode not in barcodes');
                    if not sn in sns:
                        logger.debug('sn not in sns');
                        if not sn in components_sns:
                            logger.debug('sn not in components');
                            if not record.device:
                                logger.debug('and no assigned device');
                                errors.append('Brak w Ralph')
                            else:
                                paired_data = {'component_sn': sn, 'record': record, 'paired': record.device}
                        else:
                            paired_data = {'component_sn': sn, 'record': record, 'paired': GenericComponent.objects.get(sn=sn).device}

                    else:
                        try:
                            del sns_copy[sn]
                        except KeyError:
                            errors.append(['Duplikat sn w Inwent.'])
                else:
                    logger.debug('barcode is in barcodes');
                    try:
                        del barcodes_copy[barcode]
                        paired_data = {'barcode': barcode, 'record': record, 'paired': Device.objects.get(barcode=barcode)}
                    except KeyError:
                        errors.append('Duplikat barcode w Inwent.')
                    # as well
                    if sn:
                        try:
                            del sns_copy[sn]
                        except KeyError:
                            pass
            if not errors and not paired_data:
                import pdb; pdb.set_trace()
            if errors:
                yield ('error_ralph', record, errors, paired_data)
            else:
                yield ('ok', record, paired_data)

        remaining = set(barcodes_copy.values()).union(set(sns_copy.values()))
        for row in data.filter(id__in=remaining).values('id', 'name', 'venture__name', 'venture__symbol', 'barcode', 'sn'):
            yield ('error_inwent', row)


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

