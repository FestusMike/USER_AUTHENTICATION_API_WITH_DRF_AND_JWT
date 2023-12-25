from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from main.models import Project, CustomUser
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, logout
from django.contrib.auth.hashers import make_password
from .serializers import RegisterSerializer, LoginSerializer, ProjectSerializer, CustomUserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from sib_api_v3_sdk.rest import ApiException
import sib_api_v3_sdk
import os

@api_view(['GET'])
def getRoutes(request):
    routes = [
        {'GET': 'api/projects/'},
        {'GET': 'api/projects/<uuid:pk>/'},
        {'POST': 'api/projects/add/'},
        {'PUT/PATCH': 'api/projects/edit/<uuid:pk>/'},
        {'DELETE': 'api/projects/delete/<uuid:pk>/'},

        {'POST': 'api/register/'},
        {'POST': 'api/login/'},
        {'POST': 'api/logout/'},
        
        {'GET': 'api/users/'},
        {'GET': 'api/users/<uuid:pk>/'},
        
    ]
    return Response(routes)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        existing_user = CustomUser.objects.filter(email=email).first()
        if existing_user:
            return Response({'error': 'User with this email already exists'}, status=400)
        raw_password = serializer.validated_data['password']
        hashed_password = make_password(raw_password)
        user = serializer.save(password=hashed_password)        
        response_data = {
            'message': 'Congratulations! Your registration was successful. A welcome notification has been sent to {}. Welcome Aboard.'.format(user.email),
        }
        try:
            # Set up Sendinblue API configuration
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key['api-key'] = os.environ.get('EMAIL_API_KEY')
            api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
            # Define email parameters
            subject = "Welcome to UserAuthAPI!"
            sender = {"name" : 'UserAuthApi', "email": os.environ.get('EMAIL_SENDER')}
            reply_to = {"email": os.environ.get('EMAIL_REPLY_TO')}
            html_content = f"<html><body><h3>Welcome, {user.username}!</h3> <small>I am happy to have you here.</small></body></html>"
            to = [{"email": user.email, "name": user.username}]
            # Create an instance of SendSmtpEmail
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, reply_to=reply_to, html_content=html_content, sender=sender, subject=subject)
            # Send the transactional email
            api_response = api_instance.send_transac_email(send_smtp_email)
            print(api_response)
        except ApiException as e:
            print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
        return Response(response_data)
    else:
        error_message = 'Invalid or Existing registration data. Please check your input.'
        return Response({'error': error_message}, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            return Response({'access_token': access_token, 'refresh_token': refresh_token}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    logout(request)
    return Response({'message': 'User logged out successfully'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getProjects(request):
    projects = Project.objects.all()
    serialize = ProjectSerializer(projects, many=True)
    response_data = {
        'message' : '{} projects retrieved successfully'.format(len(projects)),
        'status' :  status.HTTP_200_OK,
        'data' : serialize.data
    }
    return Response(response_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getProjectById(request, pk):
    project = get_object_or_404(Project, project_id=pk)
    serializer = ProjectSerializer(project)
    response_data = {
        'message': 'Project retrieved successfully',
        'status': status.HTTP_200_OK,
        'data': serializer.data
    }
    return Response(response_data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createProject(request):
    owner = request.user
    serialize = ProjectSerializer(data=request.data)    
    if serialize.is_valid():
        serialize.validated_data['project_owner'] = owner
        serialize.save()
        response_data = {
            'message': 'Your project with the title "{}" has been uploaded successfully'.format(
                serialize.validated_data['title']
            ),
        }
        return Response(response_data)
    else:
        return Response(serialize.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def editProject(request, pk):
    project_instance = get_object_or_404(Project, project_id=pk)
    if request.user != project_instance.project_owner:
        return Response({'error': 'You do not have permission to edit this project'}, status=status.HTTP_403_FORBIDDEN)
    serializer = ProjectSerializer(project_instance, data=request.data, partial=request.method == 'PATCH')
    if serializer.is_valid():
        serializer.save()
        response_data = {
            'message': 'Your project with the title "{}" has been edited successfully'.format(
                serializer.validated_data['title']
            ),
        }
        return Response(response_data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteProject(request, pk):
    project_instance = get_object_or_404(Project, project_id=pk)
    if request.user != project_instance.project_owner:
        return Response({'error': 'You do not have permission to delete this project'}, status=status.HTTP_403_FORBIDDEN)
    serializer = ProjectSerializer(project_instance)
    project_instance.delete()
    response_data = {
        'message': 'Your project with the title "{}" has been deleted successfully'.format(
            serializer.data['title']
        ),
    }
    return Response(response_data, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUsers(request):
    users = CustomUser.objects.all().order_by('-date_created')
    serialize = CustomUserSerializer(users, many=True)
    response_data = {
        'message' : '{} users retrieved successfully'.format(len(users)),
        'status' :  status.HTTP_200_OK,
        'data' : serialize.data
    }
    return Response(response_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserById(request, pk):
    try:
        user = CustomUser.objects.get(id=pk)
        serializer = CustomUserSerializer(user)
        response_data = {
            'message': 'User retrieved successfully',
            'status': status.HTTP_200_OK,
            'data': serializer.data
        }
        return Response(response_data)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)