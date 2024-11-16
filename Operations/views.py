from django.shortcuts import render
import json
from django.http import JsonResponse
from ATP.views import update_eng_location, update_eng_location_fail
from ATP.models import EngLocation, BomList, Locations
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils import timezone
from Common.logging_config import setup_logger
import logging, inspect

logger = setup_logger(__name__)


def log_with_context(message, level=logging.INFO):
    # Get the caller's frame
    frame = inspect.currentframe().f_back
    module = inspect.getmodule(frame).__name__
    func_name = frame.f_code.co_name
    logger.log(level, f"Module: {module} - Function: {func_name} - Message: {message} ")

def get_esn_data(request):
    global cur_location, location, pass_location, fail_desc, conversion, inspection

    if request.method == 'GET':
        esn = request.GET.get('esn', '')

        # Initialize default response status and message
        status = 'error'
        message = 'Failed to process the request'
        data = {}

        # Retrieve EngLocation data
        try:
            cur_location = get_object_or_404(EngLocation, esn=esn)
            inspection = cur_location.insp_type
            conversion = cur_location.for_conversion
        except Exception as e:
            logger.error(f"Error retrieving EngLocation with ESN {esn}: {e}")
            return JsonResponse({'status': status, 'message': f"Error retrieving EngLocation with ESN {esn}: {e}"})

        # Retrieve location data
        try:
            location = get_object_or_404(Locations, loc_id=cur_location.cur_loc)
            pass_location = get_object_or_404(Locations, loc_id=location.pass_field)
        except Exception as e:
            logger.error(f"Error retrieving Locations with cur_loc {cur_location.cur_loc}: {e}")
            return JsonResponse(
                {'status': status, 'message': f"Error retrieving Locations with cur_loc {cur_location.cur_loc}: {e}"})

        # Retrieve fail description if applicable
        fail_desc = '-- NA --'
        if location.fail:
            try:
                fail_desc = get_object_or_404(Locations, loc_id=location.fail).location_desc
            except Exception as e:
                logger.error(f"Error retrieving fail location with loc_id {location.fail}: {e}")
                fail_desc = '-- NA --'

        # Retrieve BOM instance
        try:
            bom_instance = BomList.objects.get(bom=cur_location.bom)
        except BomList.DoesNotExist:
            logger.error(f"Error retrieving BOM with bom {cur_location.bom}: BOM does not exist")
            bom_instance = None

        if bom_instance:
            data = {
                'cur_location_no': cur_location.cur_loc,
                'esn': esn,
                'bom': bom_instance.bom,
                'description': bom_instance.description,
                'model': bom_instance.model,
                'type': bom_instance.type,
                'series': bom_instance.series,
                'loc_name': location.location_desc,
                'activity': location.activity,
                'pass_loc': pass_location.location_desc,
                'fail': fail_desc,
                'conversion': conversion,
                'inspection': inspection,
            }
            status = 'success'
            message = 'Successfully returned API request'
        else:
            message = 'Failed to retrieve BOM data'

        print(data)

        log_with_context(f'Transferred ESN {esn} detail at current operation', level=logging.INFO)

        return JsonResponse({
            'status': status,
            'data': data,
            'message': message
        })
@csrf_exempt
def update_location(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        esn = data['esn']
        loc_name = data['loc_name']

        current_location = get_object_or_404(Locations, location_desc=loc_name)
        log_with_context(f'Update request received for {esn}', level=logging.INFO)

        if 'fail' in data and data['fail'] != '-- NA---':
            fail_loc = data['fail']
            fail_location = get_object_or_404(Locations, location_desc=fail_loc)
            update_eng_location_fail(
                esn,
                f"st{fail_location.loc_id}_status", True,
                f"st{fail_location.loc_id}_date", timezone.now(),
                "cur_loc", fail_location.loc_id,
                f"st{current_location.loc_id}_status", False
            )
            log_with_context(f'Esn {esn} set for Rework/Hold at st{fail_location.loc_id}_status', level=logging.INFO)

        if 'pass_loc' in data:
            next_loc = data['pass_loc']
            next_location = get_object_or_404(Locations, location_desc=next_loc)
            update_eng_location(
                esn,
                f"st{next_location.loc_id}_status", True,
                f"st{next_location.loc_id}_date", timezone.now(),
                "cur_loc", next_location.loc_id
            )
            log_with_context(f'Esn {esn} next operation set at st{next_location.loc_id}_status', level=logging.INFO)

        return JsonResponse({'status': 'success', 'message': 'Operation updated successfully'})



