

# TODO: add media serializers later : media, verification, admin override
from rest_framework import serializers
from core.models import (SiteMetadata, SiteVerificationVote, HeritageSite,
                         VerificationLog, User, SiteSettings)
from user.serializers import UserSerializer


class SiteMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteMetadata
        fields = '__all__'


class SiteVerificationVoteSerializer(serializers.ModelSerializer):

    verifier = UserSerializer(read_only=True)

    class Meta:
        model = SiteVerificationVote
        fields = ['id', 'site', 'verifier', 'vote', 'comment', 'created_at']
        read_only_fields = ['id', 'verifier', 'created_at']

    # def validate(self, data):
    #     """ Validate submission data """
    #     site = data.get('site')
    #     user = self.context['request'].user

    #     if SiteVerificationVote.objects.filter(site=site, verifier=user).exists():
    #         raise serializers.ValidationError(
    #             "You have already submitted a verification vote for this site.")

    #     if site.status != 'pending':
    #         raise serializers.ValidationError(
    #             "This site is not pending verification.")

    #     return data


class SiteVerificationVoteCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating verification votes"""
    class Meta:
        model = SiteVerificationVote
        fields = ['vote', 'comment']
        extra_kwargs = {'comment': {'required': False}}

    def validate(self, data):
        site = self.context['site']
        user = self.context['request'].user

        # Check if user is assigned verifier
        if not site.site_settings.verifiers.filter(id=user.id).exists():
            raise serializers.ValidationError(
                "You are not assigned as a verifier for this site"
            )

        # Check if user has already voted
        if SiteVerificationVote.objects.filter(site=site, verifier=user).exists():
            raise serializers.ValidationError(
                "You have already submitted a vote for this site"
            )

        return data


class SiteVerificationLogSerializer(serializers.ModelSerializer):
    """Serializer for audit logs"""

    changed_by = UserSerializer(read_only=True)

    class Meta:
        model = VerificationLog
        fields = ['id', 'previous_status', 'new_status', 'changed_by',
                  'is_override', 'reason', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class SiteListSerializer(serializers.ModelSerializer):
    """Thin serializer for site listings - minimal fields"""

    category_display = serializers.CharField(
        source='get_category_display', read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', read_only=True)
    created_by = UserSerializer(read_only=True)
    # verification_status = serializers.SerializerMethodField()

    class Meta:
        model = HeritageSite
        fields = [
            'id', 'site_name', 'status', 'status_display', 'category',
            'category_display', 'latitude', 'longitude', 'created_by',
            'date_created', 'last_updated',
        ]
        read_only_fields = ['id', 'date_created', 'last_updated']

    # def get_verification_status(self, obj):
    #     return obj.get_verification_status()


class VoteSubmissionSerializer(serializers.Serializer):
    """Serializer for submitting verification vote"""

    vote = serializers.ChoiceField(choices=['approve', 'reject'])
    comment = serializers.CharField(
        required=False, allow_blank=True, max_length=1000)


class SiteSettingsSerializer(serializers.ModelSerializer):
    """Serializer for site settings"""

    verifiers = UserSerializer(many=True, read_only=True)
    verifier_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True,
        source='verifiers'
    )

    class Meta:
        model = SiteSettings
        fields = ['required_verifier_count', 'verifiers', 'verifier_ids']

    def validate_required_verifier_count(self, value):
        """Ensure reasonable verifier count"""
        if value < 1:
            raise serializers.ValidationError("Minimum 1 verifier required")
        if value > 10:
            raise serializers.ValidationError("Maximum 10 verifiers allowed")
        return value


class SiteDetailSerializer(serializers.ModelSerializer):
    """Full serializer for site detail view with verification status"""

    metadata = SiteMetadataSerializer()
    category_display = serializers.CharField(
        source='get_category_display', read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', read_only=True)
    created_by = UserSerializer(read_only=True)

    site_verification_vote = SiteVerificationVoteSerializer(
        many=True, read_only=True)
    verification_status = serializers.SerializerMethodField()
    verification_logs = SiteVerificationLogSerializer(
        many=True, read_only=True)
    can_verify = serializers.SerializerMethodField()

    class Meta:
        model = HeritageSite
        fields = [
            'id', 'site_name', 'description', 'status', 'status_display',
            'category', 'category_display', 'latitude', 'longitude',
            'population_density', 'migration_route',
            'metadata', 'created_by', 'date_created', 'last_updated',
            'site_verification_vote', 'verification_status',
            'verification_logs', 'can_verify'
        ]
        read_only_fields = ['id', 'created_by', 'date_created', 'last_updated']

    # def get_verification_status(self, obj):
    #     """Get vote counts and threshold information"""
    #     return obj.get_verification_status()

    def get_can_verify(self, obj):
        """Check if current user can verify this site"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.can_user_verify(request.user)

    def get_verification_status(self, obj):
        """Get vote counts and threshold information"""
        status = obj.get_verification_status()

        # Add pending_verifiers if missing
        if 'pending_verifiers' not in status:
            from sites.models import SiteSettings
            settings = SiteSettings.load()
            status['pending_verifiers'] = settings.verifiers.exclude(
                verifications__site=obj
            ).count()

        return status


class SiteCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating sites with validation"""

    metadata = SiteMetadataSerializer()
    site_verification_vote = SiteVerificationVoteSerializer(
        many=True, read_only=True)

    class Meta:
        model = HeritageSite
        fields = [
            'site_name', 'description', 'category', 'latitude', 'longitude',
            'population_density', 'migration_route',
            'metadata', 'site_verification_vote',
        ]

    def validate_metadata(self, value):
        """Validate metadata structure"""
        required_keys = ['sensitivity_level', 'access_protocol']
        for key in required_keys:
            if key not in value:
                raise serializers.ValidationError(
                    f"Missing required metadata key: {key}")

        # Validate sensitivity level
        if value['sensitivity_level'] not in ['public', 'restricted', 'closed']:
            raise serializers.ValidationError("Invalid sensitivity level")

        return value

    def validate(self, data):
        """Cross-field validation"""
        category = data.get('category')

        # Validate category-specific requirements
        if category == 'language' and not data.get('population_density'):
            raise serializers.ValidationError(
                "Population density is required for language sites"
            )

        if category == 'migration' and not data.get('migration_route'):
            raise serializers.ValidationError(
                "Migration route is required for migration sites"
            )

        return data

    # def create(self, validated_data):
    #     """Set created_by from request context"""
    #     validated_data['created_by'] = self.context['request'].user
    #     validated_data['status'] = 'pending'
    #     return super().create(validated_data)

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['status'] = 'pending'
        metadata_data = validated_data.pop('metadata')
        metadata = SiteMetadata.objects.create(**metadata_data)
        site = HeritageSite.objects.create(metadata=metadata, **validated_data)
        return site

    def update(self, instance, validated_data):
        # Handle metadata update separately
        if 'metadata' in validated_data:
            metadata_data = validated_data.pop('metadata')
            metadata_serializer = SiteMetadataSerializer(
                instance.metadata,
                data=metadata_data,
                partial=self.partial
            )
            metadata_serializer.is_valid(raise_exception=True)
            metadata_serializer.save()

        return super().update(instance, validated_data)
