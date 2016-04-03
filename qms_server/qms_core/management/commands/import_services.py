from __future__ import print_function
import json
import tempfile
import urllib2
from zipfile import ZipFile

import os
import shutil
from django.core.management import BaseCommand

from .qms_plugin.data_source_serializer import DataSourceSerializer
from .qms_plugin.supported_drivers import KNOWN_DRIVERS
from qms_core.models import GeoService, TmsService, WmsService, WfsService

__author__ = 'yellow'


class Command(BaseCommand):
    help = 'Import existing services from github'
    output_transaction = True
    CONTRIBUTE_REPO_URL = 'https://api.github.com/repos/nextgis/quickmapservices_contrib'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Remove existing data and create new')

    def handle(self, *args, **options):
        if options['clear']:
            GeoService.objects.all().delete()

        count = 0
        services_dir = self.load_contrib_pack()
        services_dirs = os.listdir(os.path.join(services_dir, 'data_sources'))

        for s_dir in services_dirs:
            src_dir = os.path.join(services_dir, 'data_sources', s_dir)
            metadata_pth = os.path.join(src_dir, 'metadata.ini')
            ds = DataSourceSerializer.read_from_ini(metadata_pth)

            if ds.type == KNOWN_DRIVERS.TMS:
                service = TmsService(name=ds.alias,
                                     url=ds.tms_url,
                                     z_min=ds.tms_zmin,
                                     z_max=ds.tms_zmax,
                                     )

                if ds.tms_y_origin_top is not None:
                    service.y_origin_top = ds.tms_y_origin_top
                service.save()

            if ds.type == KNOWN_DRIVERS.WMS:
                service = WmsService(name=ds.alias,
                                     url=ds.wms_url,
                                     params=ds.wms_params,
                                     layers=ds.wms_layers,
                                     turn_over=ds.wms_turn_over)
                service.save()

            if ds.type == KNOWN_DRIVERS.WFS:
                service = WfsService(name=ds.alias,
                                     url=ds.wfs_url)
                service.save()

            if ds.type == KNOWN_DRIVERS.GDAL:
                print('Unsupported service type: %s %s' % (ds.type, ds.alias))
                count -= 1

            count += 1

        self.clean()
        self.stdout.write('Successfully import %s services of %s' % (count, len(services_dirs)))


    def load_contrib_pack(self):
        # get info
        latest_release_info = self._get_latest_release_info()
        name = latest_release_info['name']
        zip_url = latest_release_info['zipball_url']

        # create temp dir
        self.tmp_dir = tempfile.mkdtemp()

        # download zip file
        zip_file_path = os.path.join(self.tmp_dir, 'contrib.zip')
        self._download_file(zip_url, zip_file_path)

        # extract zip to tmp dir
        tmp_extract_dir = os.path.join(self.tmp_dir, 'contrib')
        self._extract_zip(zip_file_path, tmp_extract_dir)

        # first dir - our content
        src_dir_name = os.listdir(tmp_extract_dir)[0]
        src_dir = os.path.join(tmp_extract_dir, src_dir_name)

        return src_dir


    def clean(self):
        if self.tmp_dir and os.path.exists(self.tmp_dir):
            # remove tmp dir
            shutil.rmtree(self.tmp_dir, ignore_errors=True)


    def _get_latest_release_info(self):
        response = urllib2.urlopen('%s/%s/%s' % (self.CONTRIBUTE_REPO_URL, 'releases', 'latest'))
        latest_release_info = json.loads(response.read().decode('utf-8'))
        return latest_release_info


    def _download_file(self, url, out_path):
        d_file = urllib2.urlopen(url)
        with open(out_path, 'wb') as output:
            output.write(d_file.read())


    def _extract_zip(self, zip_path, out_path):
        zf = ZipFile(zip_path)
        zf.extractall(out_path)