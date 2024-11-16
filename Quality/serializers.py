from rest_framework import serializers
from .models import QCalAgency, QGaugeType, QLocation, QCalStatus, QGaugeData, QGaugeDataTable, QMailerList


class QCalAgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = QCalAgency
        fields = '__all__'

class QGaugeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QGaugeType
        fields = '__all__'
        # fields = ['id', 'gauge_type']  # List of fields to include in the serialization

class QLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = QLocation
        # fields = ['location', 'name', 'address', 'contact_person1', 'contact_person2','contactp_mail1', 'contactp_mail2']  # You can also specify a list of fields, e.g., ['id', 'location', 'name', ...]
        fields = '__all__'
class QCalStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = QCalStatus
        fields = '__all__'  # Include all fields in the serializer

    def validate_last_cal_date(self, value):
        # Check if the year is within a reasonable range
        if value and (value.year < 1900 or value.year > 2100):
            raise serializers.ValidationError("Invalid year for last calibration date.")
        return value

class QGaugeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = QGaugeData
        fields = '__all__'  # You can also specify specific fields as needed
        # fields = ('gauge_type_id', 'gauge_id_no', 'gauges')
        def validate_frequency(self, value):
            if value is None or value == '':
                return None  # Handle case where frequency is not provided
            try:
                return int(value)
            except ValueError:
                raise serializers.ValidationError("Frequency must be a valid integer.")

class QGaugeDataTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = QGaugeDataTable
        fields = ['gauge_id_no', 'gauges', 'unit', 'location']  # Specify the fields you want to serialize

    def create(self, validated_data):
        """Override create method to add custom create behavior if needed."""
        return QGaugeDataTable.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Override update method to add custom update behavior if needed."""
        instance.gauge_id_no = validated_data.get('gauge_id_no', instance.gauge_id_no)
        instance.gauges = validated_data.get('gauges', instance.gauges)
        instance.unit = validated_data.get('unit', instance.unit)
        instance.location = validated_data.get('location', instance.location)
        instance.save()
        return instance

class QMailerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = QMailerList
        fields = '__all__'  # This will include all fields from the model

# class QGaugeIdMailSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = QGaugeIdMail
#         fields = '__all__'  # Include all fields in the model