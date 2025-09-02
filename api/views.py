import json
import os

from django.http import HttpResponse
from drf_spectacular import renderers
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import filters, status
from rest_framework.generics import ListAPIView
from rest_framework.parsers import MultiPartParser, JSONParser, FileUploadParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

from api.serializers import JsonSerializer, UploadJsonSerializer
from json_handler.models import JSONData
from django.db.models import QuerySet

from laboratory_django import settings


def get_search_results(queryset, search_term):
    queryset |= JSONData.objects.all()
    if search_term:
        try:
            key_value_pairs = search_term.split('&&')
            json_results = []
            for obj in queryset:
                if isinstance(obj.data, dict):
                    json_data = obj.data
                else:
                    json_data = json.loads(obj.data)  # Convert the JSON string to a Python object
                try:
                    if check_key_value_pairs(json_data, key_value_pairs):
                        json_results.append(obj)
                except json.JSONDecodeError:
                    # Handle the JSON decoding error
                    pass
                queryset = JSONData.objects.filter(
                    pk__in=[item.pk for item in json_results])  # Convert the list to a queryset
        except:
            return queryset

    return queryset


def check_key_value_pairs(data, key_value_pairs):
    for key_value_pair in key_value_pairs:
        search_key, search_value = key_value_pair.split(':', 1)
        if not search_json(data, search_key, search_value):
            return False
    return True


def search_json(data, search_key, search_value):
    # Search in json key value
    if isinstance(data, dict):
        for key, value in data.items():
            if search_key.lower() == key.lower() and search_value in str(value):
                return True
            if isinstance(value, (dict, list)):
                if search_json(value, search_key, search_value):
                    return True
    elif isinstance(data, list):
        for item in data:
            if search_json(item, search_key, search_value):
                return True
    return False


@extend_schema_view(
    get=extend_schema(
        parameters=[
            # OpenApiParameter(name='q', description='Search in product titles', type=str),
            OpenApiParameter(name='owner', description='Owner', type=str),
            OpenApiParameter(name='Abaqus-Version', description='Abaqus Version', type=str),
            OpenApiParameter(name='Hash_Orientation', description='Hash Orientation', type=str),
            OpenApiParameter(name='Texture_Type', description='Texture Type', type=str),
            OpenApiParameter(name='Element_Number', description='Element Number', type=str),
            OpenApiParameter(name='Material_parameters', description='Material Parameters', type=str),
            OpenApiParameter(name='Load_Type', description='Load Type', type=str),
            OpenApiParameter(name='Stress_Type', description='Stress Type', type=str),
            OpenApiParameter(name='Load_Descriptor', description='Load Descriptor', type=str),
            OpenApiParameter(name='Hash_load', description='Hash Load', type=str),
            OpenApiParameter(name='Scaling_Factor', description='Scaling Factor', type=str),
            OpenApiParameter(name='Max_Total_Strain', description='Max Total Strain', type=str),
        ]
    )
)
@extend_schema(tags=['Json API'])
class SearchDataAPI(ListAPIView):
    permission_classes = [HasAPIKey]
    queryset = JSONData.objects.all()
    serializer_class = JsonSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        search_term = self.request.query_params
        if search_term:
            all_parameters = '&&'.join([f"{key}:{value}" for key, value in self.request.query_params.items()])
            search_results = get_search_results(queryset, all_parameters)
            return search_results
        return queryset.distinct()



@extend_schema(tags=['Json API'])
class UploadJsonAPI(APIView):
    permission_classes = [HasAPIKey]
    serializer_class = UploadJsonSerializer
    parser_classes = (MultiPartParser,)

    def post(self, request):
        serializer = UploadJsonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": "File uploaded"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Json API'], )
class DownloadJsonAPI(APIView):
    permission_classes = [HasAPIKey]
    serializer_class = JsonSerializer

    def get(self, request, pk):
        if pk is not None:
            try:
                obj = JSONData.objects.get(pk=pk)
                data = obj.data
                json_data = json.dumps(data, indent=4)

                temp_file_path = settings.MEDIA_ROOT + 'files'
                with open(temp_file_path, 'w') as f:
                    f.write(json_data)

                with open(temp_file_path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/json')
                    response['Content-Disposition'] = f'attachment; filename="{obj.pk}.json"'
                return response

            except JSONData.DoesNotExist:
                return Response({"data": "File does not exist"}, status=status.HTTP_404_NOT_FOUND)

            except Exception as e:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_400_BAD_REQUEST)
