from django.forms import ModelForm

from qms_core.models import TmsService, WmsService, WfsService, GeoJsonService


class TmsForm(ModelForm):
    associated_template = 'edit_snippets/tms_service.html'

    class Meta:
        model = TmsService
        fields = '__all__'


class WmsForm(ModelForm):
    associated_template = 'edit_snippets/wms_service.html'

    class Meta:
        model = WmsService
        fields = '__all__'


class WfsForm(ModelForm):
    associated_template = 'edit_snippets/wfs_service.html'

    class Meta:
        model = WfsService
        fields = '__all__'


class GeoJsonForm(ModelForm):
    associated_template = 'edit_snippets/geojson_service.html'

    class Meta:
        model = GeoJsonService
        fields = '__all__'
