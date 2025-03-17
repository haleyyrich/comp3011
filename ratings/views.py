from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from .models import Professor, Module, Rating
from .serializers import ProfessorSerializer, RatingSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.db.models import Avg
from django.core.exceptions import ValidationError

# user registration API - register
class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        # error handling - check if username already exists
        if User.objects.filter(username=username).exists():
            return Response({"Username already in use. Please choose a different username."}, status=status.HTTP_400_BAD_REQUEST)

         # error handling - check if email is in use
        if User.objects.filter(email=email).exists():
            return Response({"Email already in use."}, status=status.HTTP_400_BAD_REQUEST)

        # error handling - check if all fields are provided
        if not username or not email or not password:
            return Response({"All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        # successful registration
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        return Response({"Successfully registered! Please log in."}, status=status.HTTP_201_CREATED)

# auth token endpoint, for token related views
class AuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
    
# user login API - login
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        
        else:
            return Response({'error': 'Credentials are invalid. Please try logging in again.'}, status=status.HTTP_401_UNAUTHORIZED)

# user logout API - logout        
class LogoutView(APIView):
    def post(self, request):
        response = JsonResponse({'message': 'Successfully logged out!'})
        response.delete_cookie('access_token')
        return response

# list professors + modules API - list
class ListView(generics.ListAPIView):
    queryset = Professor.objects.prefetch_related('module_set').all()
    serializer_class = ProfessorSerializer

# view all ratings API - view
class ViewView(APIView):
    def get(self, request):  
        ratings = Rating.objects.select_related('professor').all()  
        data = [] 
        for rating in ratings:  
            data.append({  
                "professor": {
                    "id": rating.professor.id,
                    "name": rating.professor.name
                },
                "module": {
                    "id": rating.module.id,
                    "name": rating.module.name,
                    "year": rating.module.year,
                    "semester": rating.module.semester
                },
                "rating": rating.rating,  
                "comment": rating.comment,  
                "date": rating.date.isoformat()  
            })  

        return Response(data)  

# average professor rating API - average
class AverageView(APIView):
    def get(self, request):
        # variables
        professor_id = request.query_params.get('professor')  
        module_id = request.query_params.get('module')  

        # error handling: professor and module id must be included
        if not professor_id or not module_id:  
            return Response({"error": "Please provide both professor and module ID."}, status=400)  

        try:
            # error handling: check if the module exists
            module = Module.objects.get(id=module_id)

            # error handling: check if the professor exists in the module's ManyToManyField
            professor = Professor.objects.get(id=professor_id)
            if not module.professor.filter(id=professor_id).exists():
                return Response({"error": "Professor does not teach that module."}, status=400)

            # Query ratings for the given professor and module
            average = Rating.objects.filter(
                professor=professor,
                module=module
            ).aggregate(avg_rating=Avg('rating'))

            # error handling if no average rating is found
            if average['avg_rating'] is None:
                return Response({"error": "No ratings found for that professor in that module."}, status=404)

            return Response({
                "professor": professor_id,
                "module": module_id,
                "average_rating": round(average['avg_rating'])
            })

        except Module.DoesNotExist:
            return Response({"error": "Module not found."}, status=404)

        except Professor.DoesNotExist:
            return Response({"error": "Professor not found."}, status=404)
    
# rate a professor API - rate
class RateView(APIView):
    def post(self, request):
        # variables
        professor_id = request.data.get("professor")
        module_id = request.data.get("module")
        rating = request.data.get("rating")
        comment = request.data.get("comment", "")
        serializer = RatingSerializer(data=request.data, context={'request': request})

        # saving user request to data
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # error handling: ensure professor teaches module
        try:
            professor = Professor.objects.get(id=professor_id)
            module = Module.objects.get(id=module_id)

            if not module.professor.filter(id=professor_id).exists():
                return Response({"error": "This professor does not teach this module."}, status=400)

        except (Professor.DoesNotExist, Module.DoesNotExist):
            return Response({"error": "Invalid professor or module ID."}, status=400)

        # error handling: ensure rating is between 1-5
        if not (1 <= rating <= 5):
            return Response({"error": "Rating must be between 1 and 5."}, status=400)
  
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)