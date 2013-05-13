# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'ImportRecord.cache_version'
        db.delete_column('ralph_assets_imports_importrecord', 'cache_version')

        # Deleting field 'ImportRecord.created_by'
        db.delete_column('ralph_assets_imports_importrecord', 'created_by_id')

        # Deleting field 'ImportRecord.modified_by'
        db.delete_column('ralph_assets_imports_importrecord', 'modified_by_id')

        # Deleting field 'ImportRecord.created'
        db.delete_column('ralph_assets_imports_importrecord', 'created')

        # Deleting field 'ImportRecord.modified'
        db.delete_column('ralph_assets_imports_importrecord', 'modified')


    def backwards(self, orm):
        # Adding field 'ImportRecord.cache_version'
        db.add_column('ralph_assets_imports_importrecord', 'cache_version',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'ImportRecord.created_by'
        db.add_column('ralph_assets_imports_importrecord', 'created_by',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm['account.Profile'], blank=True, null=True),
                      keep_default=False)

        # Adding field 'ImportRecord.modified_by'
        db.add_column('ralph_assets_imports_importrecord', 'modified_by',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm['account.Profile'], blank=True, null=True),
                      keep_default=False)

        # Adding field 'ImportRecord.created'
        db.add_column('ralph_assets_imports_importrecord', 'created',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)

        # Adding field 'ImportRecord.modified'
        db.add_column('ralph_assets_imports_importrecord', 'modified',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)


    models = {
        'ralph_assets_imports.importrecord': {
            'Meta': {'object_name': 'ImportRecord'},
            'barcode': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'date': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'dc': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'deprecation_rate': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'device_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'device_type': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'errors': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'fv': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'info': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'invent_value': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'niw': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'price_netto': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'rack': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'second_sn': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'sn': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'u_height': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'u_level': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        }
    }

    complete_apps = ['ralph_assets_imports']