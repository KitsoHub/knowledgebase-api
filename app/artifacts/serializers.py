""" Serializer for Artifacts"""

from rest_framework import serializers
from core.models import Artifacts, ArtifactImages


class ArtifactImagesSerializer(serializers.ModelSerializer):
    """Serializer for Artifacts Images"""
    class Meta:
        model = ArtifactImages
        fields = ['id', 'images']
        read_only_fields = ['id']


class ArtifactsSerializer(serializers.ModelSerializer):

    images = ArtifactImagesSerializer(
        many=True, required=False, read_only=True)

    uploaded_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Artifacts
        fields = ['id', 'artifact_name', 'images',
                  'uploaded_images',]
        read_only_fields = ['id']

    def create(self, validated_data):

        images = validated_data.pop('uploaded_images', None)

        artifact = Artifacts.objects.create(**validated_data)

        if images is not None:
            ArtifactImages.objects.bulk_create(
                [ArtifactImages(artifact=artifact,
                                images=image_data) for image_data in images]
            )

        return artifact

    def update(self, instance, validate_data):
        """Override Artifacts update"""
        for attr, value, in validate_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ArtifactsDetailsSerializer(ArtifactsSerializer):

    class Meta(ArtifactsSerializer.Meta):
        fields = ArtifactsSerializer.Meta.fields + [
            'status', 'vetted_by', 'verified_by',
            'description', 'artifact_type', 'historical_significance',
            'cultural_significance'
        ]
