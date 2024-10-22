from django.contrib import admin
from .models import ComplaintTypeModel, SuggestionTypeModel, ComplaintModel, SuggestionModel


admin.site.register([ComplaintTypeModel, SuggestionTypeModel,
                    ComplaintModel, SuggestionModel])
