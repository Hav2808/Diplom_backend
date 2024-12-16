import os
import shutil
import logging
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import File
from .serializers import FileReadSerializer, FileWriteSerializer, UserSerializer,CustomUserCreateSerializer
from .utils import seconds_since_epoch
from django.utils.encoding import iri_to_uri
from rest_framework import generics
from .serializers import UserSerializer

logger = logging.getLogger('mycloud')

class UserListView(generics.ListAPIView):
    """
    View для получения всех Пользователей.

    - queryset: все объекты User, отсортированные по id.
    - serializer_class: UserSerializer.
    - permission_classes: только администраторы.
    """
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)

    def get(self, request, *args, **kwargs):
        logger.info('Fetching all users')
        return super().get(request, *args, **kwargs)

class UserDetailView(APIView):
    """
    View для удаления и изменения статуса администратора пользователя.

    - permission_classes: только администраторы.
    """
    permission_classes = (IsAdminUser,)

    def delete(self, request, pk, format=None):
        user = get_object_or_404(User, pk=pk)
        logger.info(f'Deleting user {user.id}')
        user_directory = os.path.join(settings.MEDIA_ROOT, f'user_{user.id}')
        if os.path.exists(user_directory):
            shutil.rmtree(user_directory)
        user.delete()
        logger.info(f'User {pk} deleted successfully')
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk, format=None):
        user = get_object_or_404(User, pk=pk)
        user.is_staff = not user.is_staff
        user.save()
        logger.info(f'User {user.id} admin status changed to {user.is_staff}')
        return Response(status=status.HTTP_200_OK)

class UserFileListView(APIView):
    """
    View для получения файлов конкретного пользователя.

    - permission_classes: только администраторы.
    """
    permission_classes = [IsAdminUser]

    def get(self, request, user_id, format=None):
        user = get_object_or_404(User, id=user_id)
        logger.info(f'Fetching files for user {user.id}')
        files = File.objects.filter(creator=user)
        serializer = FileReadSerializer(files, many=True)
        logger.info(f'Retrieved {len(files)} files for user {user.id}')
        return Response(serializer.data, status=status.HTTP_200_OK)

class FileAPIUpdate(generics.RetrieveUpdateAPIView):
    """
    View для чтения и обновления файлов.

    - queryset: все объекты File.
    - serializer_class: FileWriteSerializer.
    - permission_classes: только аутентифицированные пользователи.
    """
    queryset = File.objects.all()
    serializer_class = FileWriteSerializer
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        logger.info(f'Updating file {self.get_object().id}')
        return super().update(request, *args, **kwargs)

class FileAPIDestroy(generics.RetrieveDestroyAPIView):
    """
    View для удаления файлов.

    - queryset: все объекты File.
    - serializer_class: FileWriteSerializer.
    - permission_classes: только аутентифицированные пользователи.
    """
    queryset = File.objects.all()
    serializer_class = FileWriteSerializer
    permission_classes = (IsAuthenticated,)

    def perform_destroy(self, instance):
        file_id = instance.id
        file_path = instance.file.path
        super(FileAPIDestroy, self).perform_destroy(instance)
        if file_path and os.path.isfile(file_path):
            os.remove(file_path)
            logger.info(f'Destroyed file {file_id} and removed file from {file_path}')

class FileDownloadView(APIView):
    """
    View для скачивания файла по hash из модели.

    - permission_classes: доступ для всех.
    """
    permission_classes = (AllowAny,)

    def get(self, request, hash, format=None):
        try:
            file_obj = get_object_or_404(File, hash=hash)
        except Exception as e:
            return HttpResponse("File not found", status=404)

        file_path = str(file_obj.file)
        file_name = str(file_obj.name)
        logger.info(f'Download requested for file: {file_name} with hash: {hash}')
        expansion = file_name.split('.')[-1] if '.' in file_name else ''
        path_file_obj = os.path.join(settings.MEDIA_ROOT, file_path)
        
        if os.path.exists(path_file_obj):
            file_obj.date_download = seconds_since_epoch()
            file_obj.save()
            logger.info(f'File {file_name} found, preparing for download')
            with open(path_file_obj, 'rb') as file:
                response = HttpResponse(file, content_type='application/force-download')

                if not expansion:
                    file_name += '.bin'

                response['Content-Disposition'] = f'attachment; filename=' + iri_to_uri(file_name)
                logger.info(f'File {file_name} ready for download')
                return response
        else:
            logger.error(f'File not found: {path_file_obj}')
            return HttpResponse("File not found", status=404)

class UserPostList(generics.ListCreateAPIView):
    """
    View для получения и создания файлов конкретного пользователя.

    - authentication_classes: токеновая аутентификация.
    - permission_classes: только аутентифицированные пользователи.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        files = File.objects.filter(creator=user).order_by('-data_created')
        logger.info(f'Found {len(files)} files for user {user.id}')
        return files

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return FileReadSerializer
        return FileWriteSerializer

    def list(self, request, *args, **kwargs):
        user = self.request.user
        logger.info(f'Listing files for user {user.id}')
        files = self.get_queryset()
        serializer = self.get_serializer(files, many=True)
        data = {
            'isAdmin': user.is_staff,
            'files': serializer.data
        }
        logger.info(f'Listed files for user {user.id}')
        return Response(data, status=status.HTTP_200_OK)

def index(request):
    logger.info('Rendering index page')
    return render(request, 'index.html')

class UserRegistrationView(generics.CreateAPIView):
    """
    View для регистрации новых пользователей.
    """
    def post(self, request):
        logger.info("Полученные данные: %s", request.data)
    serializer_class = CustomUserCreateSerializer
    permission_classes = (AllowAny,)  