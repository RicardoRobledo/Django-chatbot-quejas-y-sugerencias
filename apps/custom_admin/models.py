from apps.base.models import BaseModel

from django.db import models


class ComplaintTypeModel(BaseModel):

    name = models.CharField(max_length=50, unique=True)
    in_use = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"


class SuggestionTypeModel(BaseModel):

    name = models.CharField(max_length=50, unique=True)
    in_use = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"


class ComplaintModel(BaseModel):

    description = models.TextField()
    complaint_type = models.ForeignKey(
        ComplaintTypeModel, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=200,)
    email = models.EmailField()

    def __str__(self):
        return f"{self.id}"


class SuggestionModel(BaseModel):

    description = models.TextField()
    suggestion_type = models.ForeignKey(
        SuggestionTypeModel, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=200,)
    email = models.EmailField()

    def __str__(self):
        return f"{self.id}"
