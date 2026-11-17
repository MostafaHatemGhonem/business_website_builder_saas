from rest_framework import serializers
from .models import Business, Membership 



class BusinessSerializer(serializers.ModelSerializer):
    user_role = serializers.SerializerMethodField()

    class Meta:
        model = Business
        fields = [
            "id",
            "user_role",
            "name",
            "slug",
            "business_type",
            "description",
            "logo",
            "phone",
            "email",
            "address",
            "currency",
            "timezone",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_user_role(self,obj):
        request = self.context.get('request')
        if request is None or not request.user.is_authenticated:
            return None 
        return obj.get_user_role(request.user)

    
class MembershipSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(
        source = 'business.name',
        read_only = True
    )

    role_display = serializers.CharField(
        source = 'get_role_display',
        read_only = True
    )

    status_display = serializers.CharField(
        source = 'get_status_display',
        read_only = True
    )
    class Meta:
        model = Membership 
        fields = [
            "id",
            "business",
            "business_name",
            "user",
            "role",
            "role_display",
            "status",
            "status_display",
            "invited_by",
            "joined_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "invited_by",
            "joined_at",
            "created_at",
            "updated_at",
        ]