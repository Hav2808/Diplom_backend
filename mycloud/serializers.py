from django.contrib.auth.models import User
from .models import File
from django.db.models import Sum
from djoser.serializers import UserCreateSerializer, TokenSerializer
from rest_framework import serializers
from .models import File
from .utils import seconds_since_epoch
import re

class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для получения всех пользователей.
    - total_files: количество файлов пользователя.
    - total_size: общий размер всех файлов пользователя.
    """
    total_files = serializers.SerializerMethodField()
    total_size = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'is_staff', 'total_files', 'total_size')

    def get_total_files(self, obj):
        """
        Возвращает количество файлов пользователя.
        """
        return File.objects.filter(creator=obj).count()

    def get_total_size(self, obj):
        """
        Возвращает общий размер всех файлов пользователя.
        """
        return File.objects.filter(creator=obj).aggregate(total_size=Sum('size'))['total_size'] or 0

class FileReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения данных из таблицы File.
    """
    class Meta:
        model = File
        fields = ('id', 'name', 'size', 'data_created', 'date_download', 'comment', 'hash')

class FileWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления файлов в таблице File.
    """
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = File
        fields = ('id', 'creator', 'name', 'file', 'size', 'data_created', 'date_download', 'comment', 'hash')

    def create(self, validated_data):
        """
        Создаёт объект File с автоматическим установлением поля size и добавлением расширения файла, если его нет.
        """
        file = validated_data['file']
        validated_data['size'] = file.size

        original_name = file.name
        name_parts = original_name.rsplit('.', 1)
        if len(name_parts) == 2:
            name, extension = name_parts
        else:
            name = name_parts[0]
            extension = ''

        if not extension:
            extension = 'bin'

        unique_name = f"{seconds_since_epoch()}_{name}.{extension}"
        validated_data['name'] = unique_name
        validated_data['file'].name = unique_name

        return super(FileWriteSerializer, self).create(validated_data)

    def to_representation(self, instance):
        """
        Возвращает представление объекта File, исключая поле file для GET запросов.
        """
        representation = super().to_representation(instance)
        if self.context['request'].method == 'GET':
            representation.pop('file', None)
        return representation

class CustomTokenSerializer(TokenSerializer):
    """
    Кастомный сериализатор для добавления поля is_staff к токену.
    """
    is_staff = serializers.BooleanField(source='user.is_staff')

    class Meta(TokenSerializer.Meta):
        fields = ('auth_token', 'is_staff')

class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Кастомный сериализатор для создания пользователя с добавлением поля first_name.
    """
    email = serializers.EmailField()

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('username', 'email', 'password', 'first_name',)

    def validate_email(self, value):
        """ Проверяет уникальность email в базе данных. """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Этот email уже используется.")
        return value

    def validate_password(self, value):
        """ Проверяет сложность пароля согласно установленным требованиям. """
        if len(value) < 6:
            raise serializers.ValidationError("Пароль должен содержать не менее 6 символов.")
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError("Пароль должен содержать как минимум одну заглавную букву.")
        if not re.search(r"[0-9]", value):
            raise serializers.ValidationError("Пароль должен содержать как минимум одну цифру.")
        if not re.search(r"[\W_]", value):
            raise serializers.ValidationError("Пароль должен содержать хотя бы один специальный символ.")
        return value

    def create(self, validated_data):
        """ Создаёт объект User с установленным паролем. """
        user = User(**validated_data)
        user.set_password(validated_data['password'])  
        user.save()
        return user
    