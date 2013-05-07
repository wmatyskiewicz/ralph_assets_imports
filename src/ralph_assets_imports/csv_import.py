# -*- coding: utf-8 -*-

import csv, codecs
from ralph.discovery.models import Device, DeviceType, GenericComponent


class UTF8Recoder(object):
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader(object):
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter(object):
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect, encoding="windows-1250", **kwds):
        # Redirect output to a queue
        import cStringIO, csv, codecs
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    count = 0
    for row in csv_reader:
        count += 1
        if count == 3:
            break
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]

def do_it():
    import copy
    virtual = {
        DeviceType.virtual_server,
        DeviceType.cloud_server,
        DeviceType.mogilefs_storage,
    }

    data = Device.objects.exclude(
        model__type__in=virtual).values_list(
                'id', 'name', 'venture', 'venture__symbol', 'barcode', 'sn', 'model__name')

    barcodes = dict([(row[4],row[0]) for row in data])
    sns = dict([((row[5] or '').lower(), row[0]) for row in data])

    data_components = GenericComponent.objects.values_list('id', 'sn')

    components_sns = dict([(row[1].lower(), row[0]) for row in data_components])
    barcodes_copy = copy.copy(barcodes)
    sns_copy = copy.copy(sns)
    # after copy

    reader = unicode_csv_reader(open('import_ralph_assets.csv'),
        delimiter=b',', quotechar=b'"')

    writer = UnicodeWriter(f=open('braki.csv', 'w'), dialect=csv.excel)

    writer.writerow(['typ bledu', 'inwent lp', 'barcode', 'sn', 'model', 'ralph link'])
    for line in reader:
        lp, model, typ, sn, barcode, szafa, poziom, wysokosc, dc, uwagi, nwi, fv, nazwa, wartosc_inv,data_przyjecia, wartosc_netto, stawka_amortyzacji, miesiecznie, uwagi, _, data_przyjecia = line
        sn = sn or ''
        sn = sn.lower()
        if not sn and not barcode:
            writer.writerow(['Brak sn oraz barcode', lp, barcode, sn, model,'',typ])
            continue

        if not barcode in barcodes:
            if not sn in sns:
                if not sn in components_sns:
                    writer.writerow(['Brak w Ralph', lp, barcode, sn, model, '', typ])
            else:
                try:
                    del sns_copy[sn]
                except KeyError:
                    writer.writerow(['Duplikat w Inwent.', lp, barcode, sn, model,'',typ])
                    continue
        else:
            try:
                del barcodes_copy[barcode]
            except KeyError:
                writer.writerow(['Duplikat w Inwent.', lp, barcode, sn, model, '', typ])
            if sn:
                try:
                    del sns_copy[sn]
                except KeyError:
                    pass

    remaining = set(barcodes_copy.values()).union(set(sns_copy.values()))
    for row in data.filter(id__in=remaining):
        #'id', 'name', 'venture', 'venture__symbol', 'barcode', 'sn')
        writer.writerow(['Brak w Inwent.', '', row[4] or '', row[5] or '', row[6] or '', 'http://ralph.office/ui/search/info/%s?' % row[0],''])

do_it()
