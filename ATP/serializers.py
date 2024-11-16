# serializers.py
# from rest_framework import serializers
# from . import models  # Import the models module, not EngCheckpoint directly
#
# class EngCheckpointSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.EngCheckpoint  # Reference the model from the models module
#         fields = '__all__'
# # serializers.py
from rest_framework import serializers
from . import models


class BomListSerializer(serializers.ModelSerializer):
    voltage = serializers.ChoiceField(choices=[
                ('24V', '24V'), ('12V', '12V')
            ])
    model = serializers.ChoiceField(choices=[
                ('3G CRDi', '3G CRDi'), ('4G CRDi', '4G CRDi'), ('6G CRDi', '6G CRDi'),
                ('3G', '3G'), ('4G', '4G'), ('6G', '6G'),
                ('D3V6', 'D3V6'), ('D3V8', 'D3V8'), ('D3V12', 'D3V12')
            ])

    class Meta:
        model = models.BomList
        exclude = ['srno']

class OperationSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Operation
        fields = '__all__'

class EngmodelSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.EngModel
        exclude = ['srno']
class EngCheckpointSerializer(serializers.ModelSerializer):
    # Define choices for the 'type' field
    type = serializers.ChoiceField(choices=[
        ('Checkbox', 'Checkbox'),
        ('Dropdown', 'Dropdown'),
        ('Textbox', 'Textbox'),
    ])

    class Meta:
        model = models.EngCheckpoint
        # fields = '__all__'
        exclude = ['checkpoint_id']

class CheckpointMapSerializer2(serializers.ModelSerializer):
    # bom = serializers.PrimaryKeyRelatedField(queryset=models.BomList.objects.using('atp').values())
    # checkpoint = serializers.PrimaryKeyRelatedField(queryset=models.EngCheckpoint.objects.using('atp').values())
    stno = serializers.PrimaryKeyRelatedField(queryset=models.Operation.objects.using('atp').values('stno'))
    # stno =list(models.Operation.objects.using('atp').values('stno'))
    # print(stno)
    # stno = serializers.SlugRelatedField(
    #     queryset=models.Operation.objects.using('atp').values('stno'),
    #     slug_field='op_name'
    # )
    bom = serializers.SlugRelatedField(
        queryset=models.BomList.objects.using('atp').values('srno'),
        slug_field='srno'
    )
    checkpoint = serializers.SlugRelatedField(
        queryset=models.EngCheckpoint.objects.using('atp').values('checkpoint'),
        slug_field='checkpoint_id'
    )
    class Meta:
        model = models.CheckpointMap  # Reference the model from the models module
        exclude = ['id']


class CheckpointMapSerializer(serializers.ModelSerializer):
    # stno = serializers.PrimaryKeyRelatedField(queryset=models.Operation.objects.using('atp').values('stno'))
    stno = serializers.SlugRelatedField(
        queryset=models.Operation.objects.using('atp').values('stno', 'op_name'),
        slug_field='op_name'
    )
    bom = serializers.SlugRelatedField(
        queryset=models.BomList.objects.using('atp').values('srno'),
        slug_field='srno'
    )
    checkpoint = serializers.SlugRelatedField(
        queryset=models.EngCheckpoint.objects.using('atp').values('checkpoint_id'),
        slug_field='checkpoint_id'
    )
    class Meta:
        model = models.CheckpointMap  # Reference the model from the models module
        exclude = ['id']
class EngineAsslyOpSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.EngineAsslyOp
        fields = '__all__'
