from rest_framework import serializers
from .models import Professor, Module, Rating

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id', 'name', 'year', 'semester']

class ProfessorSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(source='module_set', many=True)

    class Meta:
        model = Professor
        fields = ['id', 'name', 'modules']

        def get_modules(self, obj):
            return [
                {
                "id": module.id,
                "name": module.name,
                "year": module.year,
                "semester": module.semester
                }
            for module in obj.modules.all()
        ]

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['rating', 'professor', 'module', 'comment']

    
    # set user to rating from request
    def create(self, data):
        request = self.context.get('request')
        if request is None or not hasattr(request, "user"):
            raise serializers.ValidationError("Please login before rating.")
        
        data['user'] = request.user
        return super().create(data)