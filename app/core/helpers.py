"""Helper functions"""
from django.contrib.auth import get_user_model
import os
import uuid
from core import models
from PIL import Image
import tempfile


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def create_verifier(**params):
    return get_user_model().objects.create_verifier_user(**params)

# Images


def image_path(instance, filename):
    """Generates a path to the image"""
    class_name = ''

    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'
    if type(instance) == models.Artifacts:
        class_name = 'artifact'
    else:
        class_name = 'test'

    img_path = os.path.join('uploads', class_name, filename)
    return img_path


def get_image():
    """Creates and returns an image"""
    image = Image.new("RGB", (10, 10))
    file = tempfile.NamedTemporaryFile(suffix=".jpg")
    image.save(file, format='JPEG')
    _file = open(file.name, 'rb')

    return _file
