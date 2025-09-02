import json

from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from json_handler.models import JSONData


class JsonSerializer(ModelSerializer):
    name = SerializerMethodField()
    download_url = SerializerMethodField()

    class Meta:
        model = JSONData
        fields = ['name', 'author', 'upload_time', 'id', 'download_url']

    def get_download_url(self, obj):
        request = self.context.get('request')
        url = f'download/{obj.pk}'
        return request.build_absolute_uri(url)

    def get_name(self, obj):
        first_key = next(iter(obj.data.keys()))
        return first_key


class UploadJsonSerializer(ModelSerializer):
    upload = serializers.FileField()

    class Meta:
        model = JSONData
        fields = ['author', 'upload']

    def create(self, validated_data):
        new_json_file = validated_data['upload']
        try:
            new_data = json.loads(new_json_file.read())

            # Perform the saving process for new data
            for key, value in new_data.items():
                if not JSONData.objects.filter(data={key: value}).exists():
                    JSONData.objects.create(upload=new_json_file, data={key: value}, author=validated_data['author'])

        except Exception as e:
            # Handle any exceptions
            pass

        return validated_data
