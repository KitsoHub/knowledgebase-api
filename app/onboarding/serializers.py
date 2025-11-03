""" Serializer for Onboarding"""

from rest_framework import serializers
from core.models import (
    Onboarding, OnboardingNoteImages,
    OnboardingStep, OnboardingStepImages)
# import logging

# logger = logging.getLogger(__name__)

class OnboardingStepImagesSerializer(serializers.ModelSerializer):
    """Serializer for Onboarding Step Images"""
    class Meta:
        model = OnboardingStepImages
        fields = ['id', 'images']
        read_only_fields = ['id']


class OnboardingImagesSerializer(serializers.ModelSerializer):
    """Serializer for Onboarding Images"""
    class Meta:
        model = OnboardingNoteImages
        fields = ['id', 'images']
        read_only_fields = ['id']


class OnboardingStepSerializer(serializers.ModelSerializer):

    class Meta:
        model = OnboardingStep
        fields = ['id', 'step_title', 'step_description']
        read_only_fields = ['id']


class OnboardingSerializer(serializers.ModelSerializer):

    images = OnboardingImagesSerializer(
        many=True, required=False, read_only=True)

    uploaded_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True,
        required=False,
    )
    onboardingstep = OnboardingStepSerializer(
        many=True, required=False)

    class Meta:
        model = Onboarding
        fields = ['id', 'onboarding_name', 'images',
                  'uploaded_images', 'onboardingstep']
        read_only_fields = ['id']

    def create(self, validated_data):

        images = validated_data.pop('uploaded_images', None)

        steps_data = validated_data.pop('onboardingstep', [])
        note = Onboarding.objects.create(**validated_data)

        auth_user = self.context['request'].user

        OnboardingStep.objects.bulk_create(
            [OnboardingStep(
                onboarding=note, user=auth_user,
                **step) for step in steps_data])


        if images is not None:
            OnboardingNoteImages.objects.bulk_create(
                [OnboardingNoteImages(
                    note=note,
                    images=image_data) for image_data in images]
            )

        return note

    def update(self, instance, validated_data):
        """Override Onboarding update"""
        steps_data = validated_data.pop('onboardingstep', [])
        user = self.context['request'].user
        for attr, value, in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        for step_data in steps_data:
            step_id = step_data.get('id')
            if step_id:
                step = OnboardingStep.objects.get(
                    id=step_id, onboarding=instance)
                for attr, value in step_data.items():
                    setattr(instance, attr, value)
                step.save()
            else:
                OnboardingStep.objects.bulk_create(
                    [OnboardingStep(
                        onboarding=instance, user=user,
                        **step) for step in step_data])

        return instance

class OnboardingDetailsSerializer(OnboardingSerializer):

    class Meta(OnboardingSerializer.Meta):
        fields = OnboardingSerializer.Meta.fields + [
            'department', 'status', 'onboarding_type',
            'notes',
            'created_at', 'updated_at',]


class OnboardingStepDetailsSerializer(OnboardingStepSerializer):

    class Meta(OnboardingStepSerializer.Meta):
        fields = OnboardingStepSerializer.Meta.fields + [
            'created_at', 'updated_at']
