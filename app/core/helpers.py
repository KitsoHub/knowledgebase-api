"""Helper functions"""
from django.contrib.auth import get_user_model
import os
import uuid
from core import models
from PIL import Image
import tempfile
import datetime


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
    if isinstance(models.HeritageSite):
        class_name = 'heritage_site'
    elif isinstance(models.Onboarding):
        class_name = 'onboarding_notes'
    elif isinstance(models.OnboardingStep):
        class_name = 'onboarding_step_notes'
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


def document_path(instance, filename):
    """Generate a path for instance documents"""
    class_name = 'documents'
    ext = os.path.splitext(filename)[1]
    dt = datetime.datetime.now()
    milliseconds = dt.strftime('%f')[:-4]
    dt = dt.strftime('%Y-%m-%dT%H:%M:%S')
    filename = f'{uuid.uuid4()}{dt}{milliseconds}{ext}'

    return os.path.join('uploads', class_name, filename)
