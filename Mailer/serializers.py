# serializers.py

from rest_framework import serializers
#
# class EmailSerializer(serializers.Serializer):
#     subject = serializers.CharField(max_length=100)
#     message = serializers.CharField()
#     from_email = serializers.EmailField()
#     to_email = serializers.EmailField()

class EmailSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=200)
    message = serializers.CharField(max_length=1000)
    from_email = serializers.EmailField()
    to_email = serializers.ListField(child=serializers.EmailField(), required=True)
