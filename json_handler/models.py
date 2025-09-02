from django.db import models


class JSONData(models.Model):
    upload = models.FileField(upload_to='json_files/')
    author = models.CharField(max_length=150, null=True)
    data = models.JSONField(null=True, blank=True)
    upload_time = models.DateTimeField(auto_now_add=True, null=True)


    def __str__(self):
        return self.upload.name

    def json_file(obj):
        keys_list = list(obj.data.keys())
        return keys_list[0]
