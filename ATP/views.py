import base64
import inspect
import json
import logging
import os
import re
from datetime import datetime
from Common.logging_config import setup_logger
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.utils import IntegrityError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import serializers
from .models import (BomList, EngResultAudit, CheckpointMap, Operation, EngModel, EngResultHeader,
                     EngResultCheckpoints, EngCheckpoint, EngResultImages, EngLocation, Locations,
                     EngResultRework, EngineAsslyOp)
from .serializers import (EngCheckpointSerializer, CheckpointMapSerializer, BomListSerializer, EngmodelSerializer, )
from django.db.models import Q, Min, Max
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.shortcuts import get_object_or_404  # Import for convenience

from datetime import datetime

logger = setup_logger(__name__)

def log_with_context(message, level=logging.INFO):
    # Get the caller's frame
    frame = inspect.currentframe().f_back
    module = inspect.getmodule(frame).__name__
    func_name = frame.f_code.co_name
    logger.log(level, f"Module: {module} - Function: {func_name} - Message: {message} ")
def update_eng_location(esn, field_name1, field_value1, field_name2, field_value2, field_name3, field_value3):
    try:
        eng = EngLocation.objects.get(esn=esn)
        setattr(eng, field_name1, field_value1)
        setattr(eng, field_name2, field_value2)
        setattr(eng, field_name3, field_value3)
        eng.save()
        log_with_context(f'Engine status updated for Esn: {eng}', level=logging.INFO)
    except EngLocation.DoesNotExist:
        log_with_context(f"EngLocation with esn '{esn}' does not exist.", level=logging.ERROR)
    except Exception as e:
        log_with_context(f"Error updating EngLocation with esn '{esn}': {e}", level=logging.ERROR)
def update_eng_location_fail(esn, field_name1, field_value1, field_name2, field_value2, field_name3, field_value3, field_name4, field_value4):
    try:
        eng = EngLocation.objects.get(esn=esn)
        setattr(eng, field_name1, field_value1)
        setattr(eng, field_name2, field_value2)
        setattr(eng, field_name3, field_value3)
        setattr(eng, field_name4, field_value4)
        eng.save()

        logger.info(f'Engine status updated successfully for Esn: {esn}')
        log_with_context(f'Engine status updated for Esn: {eng}', level=logging.INFO)
    except EngLocation.DoesNotExist:
        log_with_context(f"EngLocation with esn '{esn}' does not exist.", level=logging.ERROR)
        raise
    except Exception as e:
        log_with_context(f"Error updating EngLocation with esn '{esn}': {e}", level=logging.ERROR)
        raise

def save_images(images, image_folder_path):
    if not os.path.exists(image_folder_path):
        os.makedirs(image_folder_path)

    for image in images:
        image_id = image['imageId']
        image_data = image['image']

        # Remove invalid characters from image_id
        sanitized_image_id = re.sub(r'[\\/*?:"<>|]', '', image_id)
        image_data = base64.b64decode(image_data.split(',')[1])
        image_file_path = os.path.join(image_folder_path, f"{sanitized_image_id}.png")
        with open(image_file_path, 'wb') as image_file:
            image_file.write(image_data)

    return True
def egn_status(esn, stno):
    global pass_loct, fail_loct, result_loct, cur_loct, check_status, activity_loct, pass_status, fail_status
    cur_loct = get_object_or_404(EngLocation, esn=esn)
    cur_loc = cur_loct.cur_loc
    check_status = "NOk"
    #
    # if int(cur_loc) == int(stno):
    check_status = "Ok"
    loc_id = get_object_or_404(Locations, loc_id=int(cur_loc))
    activity_loct = loc_id.activity
    pass_loct = loc_id.pass_field
    fail_loct = loc_id.fail
    result_loct = loc_id.result_field

    # Assuming `cur_loct` has attributes that are named dynamically based on `pass_loct` and `fail_loct`
    pass_status_attr = f"st{pass_loct}_status"
    fail_status_attr = f"st{fail_loct}_status"

    # Use `getattr` to dynamically access the attributes
    pass_status = getattr(cur_loct, pass_status_attr, None)
    fail_status = getattr(cur_loct, fail_status_attr, None)

    # Create a dictionary with the required information
    result = {
        "status": check_status,
        "cur_loct": cur_loc,
        "pass_loct": pass_loct,
        "fail_loct": fail_loct,
        "result_loct": result_loct,
        "activity": activity_loct,
        "pass_status": pass_status,
        "fail_status": fail_status
    }

    return result
def create_folder(currentTime):
    # Extract year, month, and day components
    year = currentTime.year
    month = currentTime.month
    main_folder_name = "Images"
    sub_folder_name = f"{year}_{month:02}"  # Use zero-padding for month (e.g., 05 instead of 5)
    image_folder_path = os.path.join(os.getcwd(), main_folder_name, sub_folder_name)
    os.makedirs(image_folder_path, exist_ok=True)
    return main_folder_name, sub_folder_name

@csrf_exempt
def get_drdwn_val(request):
    log_with_context(f'get_drdwn_val', level=logging.INFO)
    if request.method == 'PUT':
        log_with_context(f'get_drdwn_val is put', level=logging.INFO)
        engmodel = EngModel.objects.all().values('engmodel')
        stno = Locations.objects.exclude(activity='Operation').values('loc_id').order_by('-loc_id')

        # Construct response data
        log_with_context(f'Received dropdown value for {stno}', level=logging.INFO)
        response_data = {
            'status': 'success',
            'message': 'Value fro dropdown.',
            'engmodel': list(engmodel),
            'stno': list(stno),
        }

        return JsonResponse(response_data)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
def opn_checksheet(request):
    if request.method == 'POST':
        logger.info('POST request received')
        try:
            # Parse request data
            data = json.loads(request.body)
            logger.debug(f'Request data received: {data}')
            # Extract data from request
            esn = data.get('esn')
            stno = data.get('stno')
            emp_id = data.get('emp_id')
            result_id = f"{esn}_{stno}"
            logger.debug(f'Trigger to open checksheet for ESN: {esn}, STNO: {stno}, Emp ID: {emp_id}, Result ID generated: {result_id}')

            # Check if ESN exists in EngLocation
            try:
                eng = EngLocation.objects.get(esn=esn)
                bom = eng.bom
                bom_detail = get_object_or_404(BomList, bom=bom)
                model, type, series, description = bom_detail.model, bom_detail.type, bom_detail.series, bom_detail.description
                logger.debug(f'Bom Detail: model={model}, type={type}, series={series}, description={description}')

                cur_loct = get_object_or_404(Locations, loc_id=stno)
                pass_loct, fail_loct, result_loct, activity = cur_loct.pass_field, cur_loct.fail, cur_loct.result_field, cur_loct.activity
                logger.debug(f'Current Location: pass_loct={pass_loct}, fail_loct={fail_loct}, result_loct={result_loct}, activity={activity}')

                # Check if ESN is already submitted in EngineAsslyOp for station 10
                if stno == '10':
                    try:
                        EngineAsslyOp.objects.get(esn=esn)
                        logger.info(f'Engine {esn} is already submitted')
                        return JsonResponse({
                            'status': 'error',
                            'message': f'Checksheet for Engine: {esn} at station: {stno} already submitted'
                        })
                    except EngineAsslyOp.DoesNotExist:
                        logger.debug(f'Checksheet not found for ESN {esn} at STNO {stno}')

                        if activity == "Check":
                            checkpoints = CheckpointMap.objects.filter(
                                stno=stno,
                                map_status=True
                            ).values(
                                'checkpoint__checkpoint_id',
                                'checkpoint__checkpoint',
                                'seq_no',
                                'checkpoint__type',
                                'checkpoint__options',
                            )
                            header_data = {
                                'esn': esn,
                                'engmodel': model,
                                'stno': stno,
                                'bom': bom,
                                'type': type,
                                'series': series,
                                'description': description
                            }
                            logger.debug(f'Checkpoints retrieved: {list(checkpoints)}')
                            return JsonResponse({
                                'status': 'success',
                                'header_data': header_data,
                                'checkpoints': list(checkpoints),
                                'activity': activity,
                                'message': 'Checksheet form data sent'
                            })

                        if activity in ["Audit", "Rework"]:
                            header_data = {
                                'esn': esn,
                                'engmodel': model,
                                'stno': result_loct,
                                'bom': bom,
                                'type': type,
                                'series': series,
                                'description': description
                            }
                            logger.debug(f'Engine Result data: {header_data}')
                            return JsonResponse({
                                'status': 'success',
                                'message': f'Engine Result to open for {activity}.',
                                'header_data': header_data,
                                'activity': activity
                            })

                if stno == '30':
                    try:
                        EngResultHeader.objects.get(result_id=result_id)
                        logger.info(f'Checksheet for ESN {esn} at STNO {stno} already submitted')
                        return JsonResponse({
                            'status': 'error',
                            'message': f'Checksheet for Engine: {esn} at station: {stno} already submitted'
                        })
                    except EngResultHeader.DoesNotExist:
                        logger.debug(f'Checksheet not found for ESN {esn} at STNO {stno}')

                        if activity == "Check":
                            checkpoints = CheckpointMap.objects.filter(
                                stno=stno,
                                map_status=True
                            ).values(
                                'checkpoint__checkpoint_id',
                                'checkpoint__checkpoint',
                                'seq_no',
                                'checkpoint__type',
                                'checkpoint__options',
                            )
                            header_data = {
                                'esn': esn,
                                'engmodel': model,
                                'stno': stno,
                                'bom': bom,
                                'type': type,
                                'series': series,
                                'description': description
                            }
                            logger.debug(f'Checkpoints retrieved: {list(checkpoints)}')
                            return JsonResponse({
                                'status': 'success',
                                'header_data': header_data,
                                'checkpoints': list(checkpoints),
                                'activity': activity,
                                'message': 'Checksheet form data sent'
                            })

                        if activity in ["Audit", "Rework"]:
                            header_data = {
                                'esn': esn,
                                'engmodel': model,
                                'stno': result_loct,
                                'bom': bom,
                                'type': type,
                                'series': series,
                                'description': description
                            }
                            logger.debug(f'Engine Result data: {header_data}')
                            return JsonResponse({
                                'status': 'success',
                                'message': f'Engine Result to open for {activity}.',
                                'header_data': header_data,
                                'activity': activity
                            })

                elif stno == '10':
                    try:
                        EngResultHeader.objects.get(result_id=f"{esn}_30")
                        logger.info(f'Engine {esn} already submitted at station 30')
                        return JsonResponse({
                            'status': 'error',
                            'message': f'Checksheet for Engine: {esn} already submitted at station 30'
                        })

                    except EngResultHeader.DoesNotExist:
                        logger.debug(f'Checksheet not found for ESN {esn} at STNO {stno}')

                        if activity == "Check":
                            checkpoints = CheckpointMap.objects.filter(
                                stno=stno,
                                map_status=True
                            ).values(
                                'checkpoint__checkpoint_id',
                                'checkpoint__checkpoint',
                                'seq_no',
                                'checkpoint__type',
                                'checkpoint__options',
                            )
                            header_data = {
                                'esn': esn,
                                'engmodel': model,
                                'stno': stno,
                                'bom': bom,
                                'type': type,
                                'series': series,
                                'description': description
                            }
                            logger.debug(f'Checkpoints retrieved: {list(checkpoints)}')
                            return JsonResponse({
                                'status': 'success',
                                'header_data': header_data,
                                'checkpoints': list(checkpoints),
                                'activity': activity,
                                'message': 'Checksheet form data sent'
                            })

                        if activity in ["Audit", "Rework"]:
                            header_data = {
                                'esn': esn,
                                'engmodel': model,
                                'stno': result_loct,
                                'bom': bom,
                                'type': type,
                                'series': series,
                                'description': description
                            }
                            logger.debug(f'Engine Result data: {header_data}')
                            return JsonResponse({
                                'status': 'success',
                                'message': f'Engine Result to open for {activity}.',
                                'header_data': header_data,
                                'activity': activity
                            })

                elif stno == '12':
                    try:
                        # Check if ESN is in EngineAsslyOp
                        engine_assly_op = EngineAsslyOp.objects.filter(esn=esn).first()
                        if engine_assly_op:
                            logger.info(f'Checksheet for ESN {esn} at station 12 found')
                            # Check hold_status from engine_assly_op
                            hold_status = engine_assly_op.hold_status if engine_assly_op else False
                            logger.debug(f'Hold status for ESN {esn} at station 12: {hold_status}')
                            if hold_status:
                                logger.debug(f'Hold status is True for ESN {esn} at station 12')
                                if activity == "Check":
                                    checkpoints = CheckpointMap.objects.filter(
                                        map_status=True
                                    ).values(
                                        'checkpoint__checkpoint_id',
                                        'checkpoint__checkpoint',
                                        'seq_no',
                                        'checkpoint__type',
                                        'checkpoint__options',
                                    )
                                    header_data = {
                                        'esn': esn,
                                        'engmodel': model,
                                        'stno': stno,
                                        'bom': bom,
                                        'type': type,
                                        'series': series,
                                        'description': description
                                    }

                                    logger.debug(f'Checkpoints retrieved: {list(checkpoints)}')
                                    return JsonResponse({
                                        'status': 'success',
                                        'header_data': header_data,
                                        'checkpoints': list(checkpoints),
                                        'activity': activity,
                                        'message': 'Checksheet form data sent'
                                    })

                                if activity in ["Audit", "Rework"]:
                                    header_data = {
                                        'esn': esn,
                                        'engmodel': model,
                                        'stno': result_loct,
                                        'bom': bom,
                                        'type': type,
                                        'series': series,
                                        'description': description
                                    }
                                    logger.debug(f'Engine Result data: {header_data}')
                                    return JsonResponse({
                                        'status': 'success',
                                        'message': f'Engine Result to open for {activity}.',
                                        'header_data': header_data,
                                        'activity': activity
                                    })
                            else:
                                logger.debug(f'Hold status is False for ESN {esn} at station 12')
                                # Check if there is an entry for the same ESN at station 10
                                if EngineAsslyOp.objects.filter(esn=esn).exists():
                                    logger.info(f'Checksheet for ESN {esn} has already been submitted from station 10')
                                    return JsonResponse({
                                        'status': 'error',
                                        'message': f'Checksheet for Engine: {esn} is already submitted from station 10'
                                    })

                                else:
                                    logger.info(f'No submission found for ESN {esn} at station 10')
                                    return JsonResponse({
                                        'status': 'error',
                                        'message': f'Checksheet for Engine: {esn} at station 12 cannot be opened because the hold status is false'
                                    })

                        else:
                            logger.info(f'Checksheet for ESN {esn} at station 12 not found')
                            return JsonResponse({
                                'status': 'error',
                                'message': f'Checksheet for Engine: {esn} at station: {stno} not found'
                            })

                    except Exception as e:
                        logger.error(f'Error processing request for station 12: {str(e)}', exc_info=True)
                        return JsonResponse({
                            'status': 'error',
                            'message': f'An internal server error occurred: {str(e)}'
                        }, status=500)

            except EngLocation.DoesNotExist:
                logger.error(f'Engine {esn} not found')
                return JsonResponse({
                    'status': 'error',
                    'message': f'Engine {esn} is not found in records'
                })

        except json.JSONDecodeError as e:
            logger.error(f'Error decoding JSON: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)

        except Exception as e:
            logger.error(f'Error processing request: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': 'An error occurred'
            }, status=500)

    else:
        logger.error('Method not allowed')
        return JsonResponse({
            'status': 'error',
            'message': 'Method not allowed'
        }, status=405)

    # Default return in case no condition is met
    return JsonResponse({
        'status': 'error',
        'message': 'Unhandled case occurred in processing the request'
    }, status=500)


@csrf_exempt
def opn_checksheet_R2(request):
    global location

    if request.method == 'POST':
        logger.info('POST request received')
        try:
            # Parse request data
            data = json.loads(request.body)
            logger.info(f'Request data received: {data}')

            # Extract data from request
            esn = data.get('esn')
            stno = data.get('stno')
            emp_id = data.get('emp_id')
            result_id = f"{esn}_{stno}"
            logger.info(f'Trigger to open checksheet for ESN: {esn}, STNO: {stno}, Emp ID: {emp_id}, Result ID generated: {result_id})')

            # Check if ESN exists in EngLocation
            try:
                eng = EngLocation.objects.get(esn=esn)

                location = eng.cur_loc
                bom = eng.bom

                bom_detail = get_object_or_404(BomList, bom=bom)
                model, type, series, description = bom_detail.model, bom_detail.type,\
                    bom_detail.series, bom_detail.description

                cur_loct = get_object_or_404(Locations, loc_id=int(stno))
                pass_loct, fail_loct, result_loct, activity = cur_loct.pass_field, cur_loct.fail, cur_loct.result_field, cur_loct.activity
                logger.info(f'Location status for ESN {esn}: {location}')

                # Check if engine is available at requested station number (stno)
                if int(location) == int(stno):
                    try:
                        # Check if checksheet is already submitted for this result_id
                        EngResultHeader.objects.get(result_id=result_id)
                        logger.info(f'Checksheet already submitted for ESN {esn} at STNO {stno}')
                        return JsonResponse({
                            'status': 'error',
                            'message': f'Checksheet for Engine: {esn} at station: {stno} already submitted'
                        })
                    except ObjectDoesNotExist:
                        logger.info(f'Request to open Checksheet form for ESN {esn} at STNO {stno} for {activity}')
                        if activity == "Check":
                            # Fetch checkpoints for the requested station (stno)
                            checkpoints = CheckpointMap.objects.filter(
                                stno=stno,
                                map_status=True
                            ).values(
                                'checkpoint__checkpoint_id',
                                'checkpoint__checkpoint',
                                'seq_no',
                                'checkpoint__type',
                                'checkpoint__options',
                            )
                            # Prepare header data
                            header_data = {
                                'esn': esn,
                                'engmodel': model,
                                'stno': stno,
                                'bom': bom,
                                'type' : type,
                                'series' :series,
                                'description' : description
                            }

                            logger.info(f'Checkpoints retrieved: {list(checkpoints)}')
                            # Return JSON response with success status and data
                            return JsonResponse({
                                'status': 'success',
                                'header_data': header_data,
                                'checkpoints': list(checkpoints),
                                'activity' : activity,
                                'message': 'Checksheet form data sent'
                            })

                        if activity == "Audit":
                            header_data = {
                                'esn': esn,
                                'engmodel': model,
                                'stno': result_loct,
                                'bom': bom,
                                'type' : type,
                                'series' :series,
                                'description' : description
                            }
                            return JsonResponse({'status': 'success',
                            'message': 'Engine Result to open for Audit.',
                            'header_data': header_data,
                            'activity' : activity })

                        if activity == "Rework":
                            header_data = {
                                'esn': esn,
                                'engmodel': model,
                                'stno': result_loct,
                                'bom': bom,
                                'type' : type,
                                'series' :series
                            }
                            return JsonResponse({'status': 'success',
                            'message': 'Engine Result to open for Audit.',
                            'header_data': header_data,
                            'activity' : activity })

                else:
                    logger.info(f'Engine {esn} is available at location {location}, not at STNO {stno}')
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Engine {esn} is available at location {location}, not at station {stno}'
                    })

            except EngLocation.DoesNotExist:
                logger.info(f'Engine {esn} is not found in records')
                return JsonResponse({
                    'status': 'error',
                    'message': f'Engine {esn} is not found in records'
                })


        except json.JSONDecodeError as e:
            logger.error(f'Error decoding JSON: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)


        except Exception as e:
            logger.error(f'Error processing request: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': 'An error occurred'
            }, status=500)

    else:
        logger.error('Method not allowed')
        return JsonResponse({
            'status': 'error',
            'message': 'Method not allowed'
        }, status=405)

@csrf_exempt
def checksheet_data(request):
    if request.method == 'POST':
        try:
            log_with_context("Starting transaction", level=logging.INFO)

            # Log the size of the raw request body
            raw_request_body = request.body
            request_body_size = len(raw_request_body)
            log_with_context(f'Size of raw request body: {request_body_size} bytes', level=logging.INFO)

            # Parse request body JSON
            data = json.loads(raw_request_body.decode('utf-8'))

            # Optionally, log the size of the parsed data
            parsed_data_size = len(json.dumps(data))
            log_with_context(f'Size of parsed request data: {parsed_data_size} bytes', level=logging.INFO)

            checkpoint_data_list = data.get('checkpointData', [])
            image_list = data.get('images', [])
            esn = data.get('esn', '')
            engtype = data.get('engtype', '')
            username = data.get('userName', '')
            currentTime = data.get('currentTime', '')
            currentTime = datetime.strptime(currentTime, "%m/%d/%Y, %I:%M:%S %p")
            userId = data.get('userId', '')
            stno = data.get('stno', '')
            remark = data.get('remark', '')
            log_with_context(f'for debugging {currentTime}, {stno}, {userId}', level=logging.INFO)

            with transaction.atomic():

                log_with_context(f'Received Checksheet form from client for {esn} at {stno}', level=logging.INFO)
                image_dict = {image['imageId']: image['image'] for image in image_list}
                main_folder_name, sub_folder_name = create_folder(currentTime)
                image_folder_path = os.path.join(os.getcwd(), main_folder_name, sub_folder_name)
                os.makedirs(image_folder_path, exist_ok=True)
                save_images(image_list, image_folder_path)
                log_with_context("Checksheet images saved successfully", level=logging.INFO)

                result_id = f"{esn}_{stno}"
                esn_instance = EngLocation.objects.get(esn=esn)
                bom_instance  = BomList.objects.get(bom=esn_instance.bom)
                header_instance = EngResultHeader(
                    result_id=result_id,
                    esn=esn,
                    stno=stno,
                    bom_srno_id = bom_instance.srno,
                    timestamp=currentTime,
                    emp_id=userId,
                    username=username,
                    remark=remark,
                )
                header_instance.save()
                log_with_context(f"Header data for result ID {result_id} stored in DB.", level=logging.INFO)

                # Write checkpoint data to EngResultCheckpoints model
                result_instance = EngResultHeader.objects.get(result_id=result_id)
                for item in checkpoint_data_list:
                    index = item.get('index', '')
                    checkpoint_id = item.get('checkpointId', '')
                    checkpoint_status = item.get('checkpointId_Status', '')

                    checkpoint_instance = EngCheckpoint.objects.get(pk=checkpoint_id)
                    data_id = f"{esn}{stno}{checkpoint_id}"
                    checkpoint_instance = EngResultCheckpoints(
                        result=result_instance,
                        data_id=data_id,
                        checkpoint=checkpoint_instance,
                        checkpoint_status=checkpoint_status,
                        seq_no=index
                    )
                    checkpoint_instance.save()
                    log_with_context(f"Checksheet form stored in DB for checkpoint ID {checkpoint_id}",
                                     level=logging.INFO)

                # Write image data to EngResultImages model
                for image_id, image in image_dict.items():
                    result_instance = EngResultHeader.objects.get(result_id=result_id)
                    image_instance = EngResultImages(
                        result=result_instance,
                        image_id=image_id,
                        directory=sub_folder_name,
                    )
                    image_instance.save()
                    log_with_context(f"Checksheet images for result {result_id} stored in DB.", level=logging.INFO)

                eng = get_object_or_404(EngLocation, esn = esn)
                location = eng.cur_loc
                cur_loct = get_object_or_404(Locations, loc_id=int(stno))
                pass_loct = cur_loct.pass_field

                field_name1 = f"st{pass_loct}_status"
                field_value1 = True  # Example value
                field_name2 = f"st{pass_loct}_date"
                field_value2 = timezone.now()
                field_name3 = "cur_loc"
                field_value3 = int(pass_loct)  # Example value
                update_eng_location(esn, field_name1, field_value1, field_name2, field_value2, field_name3,
                                    field_value3)
                log_with_context(f"Engine moved to location {pass_loct}", level=logging.INFO)

                logging.debug("Committing transaction")
                return JsonResponse({'status': 'success', 'message': 'Form submitted and data saved.'})

        except IntegrityError as e:
            message = str(e)
            log_with_context(f'Error processing Checksheet form1: {e}', level=logging.ERROR)
            transaction.rollback()
            return JsonResponse({'status': 'error', 'message': message}, status=500)

        except Exception as e:
            message = str(e)
            log_with_context(f'Error processing Checksheet form2: {message}', level=logging.ERROR)
            log_with_context("Rolling back transaction due to unexpected error", level=logging.ERROR)
            transaction.rollback()
            return JsonResponse({'status': 'error', 'message': message}, status=500)

    else:
        log_with_context('Checksheet form not received from client', level=logging.ERROR)
        return JsonResponse({'status': 'error', 'message': 'Form not received'}, status=405)

@csrf_exempt
def opn_rework_checksheet(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        esn = int(data['esn'])
        stno = int(data['stno'])
        cur_loct = get_object_or_404(Locations, loc_id=int(stno))
        result_loct = cur_loct.result_field
        result_id = f"{esn}_{result_loct}"

        rslt_header = EngResultHeader.objects.filter(result_id=result_id).select_related('bom_srno').values(
            'result_id',
            'esn',
            'stno',
            'timestamp',
            'emp_id',
            'username',
            'remark',
            'bom_srno__model',
            'bom_srno__description',
            'bom_srno__series'
        )

        eng_checkpoints = EngResultCheckpoints.objects.filter(result_id=result_id).select_related(
            'checkpoint').values('result_id', 'checkpoint_status','seq_no' , 'checkpoint__checkpoint_id',
                                 'checkpoint__checkpoint')

        rslt_image = EngResultImages.objects.filter(result_id = result_id).values( 'image_id', 'directory')
        rslt_image_list = list(rslt_image.values())

        # Get list of Images
        base64_images = []
        for item in rslt_image_list:
            # Remove slashes from date
            image_id = re.sub(r'/', '', item['image_id'])
            image_id = re.sub(r':', '', image_id)

            # Check for .jpeg or .png extension
            possible_extensions = ['.jpeg', '.png']
            image_data = None

            for ext in possible_extensions:
                image_filename = image_id + ext
                image_path = os.path.join(os.getcwd(), 'Images', item['directory'], image_filename)

                if os.path.exists(image_path):
                    with open(image_path, "rb") as image_file:
                        image_data = image_file.read()
                    break

            if image_data:
                base64_image = base64.b64encode(image_data).decode('utf-8')
                base64_images.append(base64_image)
            else:
                print(f"Image {image_id} with extensions {possible_extensions} not found.")


        result_id = f"{esn}_{result_loct}_0"
        audit_comment = EngResultAudit.objects.filter(result_id = result_id).values('esn', 'stno', 'timestamp',
                            'emp_id', 'username', 'remark')

        # Construct response data
        response_data = {
            'status': 'success',
            'message': 'Engine Result to open.',
            'header_data': list(rslt_header),
            'checkpoint_data': list(eng_checkpoints),
            'audit_comment' : list(audit_comment),
            'images': base64_images
        }

        return JsonResponse(response_data)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def rework_checksheet(request):
    if request.method == 'POST':
        try:
            log_with_context("Starting transaction", level=logging.INFO)

            # Log the size of the raw request body
            raw_request_body = request.body
            request_body_size = len(raw_request_body)
            log_with_context(f'Size of raw request body: {request_body_size} bytes', level=logging.INFO)

            # Parse request body JSON
            data = json.loads(request.body)
            parsed_data_size = len(json.dumps(data))
            log_with_context(f'Size of parsed request data: {parsed_data_size} bytes', level=logging.INFO)
            stno = data.get('stno', '')
            esn = data.get('esn', '')
            emp_id = data.get('userId', '')
            remark = data.get('remark', '')
            username = data.get('userName', '')
            currentTime = data.get('currentTime', '')
            result_id = f"{esn}_{stno}"

            # Check if the rework checksheet already exists
            if EngResultRework.objects.filter(result_id=result_id).exists():
                log_with_context(f'Rework Checksheet already submitted for ESN {esn} at STNO {stno}', level=logging.INFO )
                return JsonResponse({
                    'status': 'error',
                    'message': f'Rework Checksheet already submitted for ESN {esn} at STNO {stno}'
                })
            with transaction.atomic():
                # Log receipt of Checksheet form
                log_with_context(f'Received Rework sheet form from client for {esn} at {stno}', level=logging.INFO)
                header_instance = EngResultRework(
                    result_id=result_id,
                    esn=esn,
                    stno=int(stno),
                    timestamp=currentTime,
                    emp_id=emp_id,
                    username=username,
                    remark=remark,
                )
                header_instance.save()
                log_with_context(f"Audit Check data for result ID {result_id} stored in DB.", level=logging.INFO)

                eng = get_object_or_404(EngLocation, esn = esn)
                location = eng.cur_loc
                cur_loct = get_object_or_404(Locations, loc_id=int(stno))
                pass_loct = cur_loct.pass_field

                field_name1 = f"st{pass_loct}_status"
                field_value1 = True  # Example value
                field_name2 = f"st{pass_loct}_date"
                field_value2 = timezone.now()
                field_name3 = "cur_loc"
                field_value3 = int(pass_loct)

                update_eng_location(esn, field_name1, field_value1, field_name2, field_value2, field_name3,
                                        field_value3)

            return JsonResponse({'status': 'success', 'message': 'Form submitted and data saved.'})

        except IntegrityError as e:
            message = str(e)
            log_with_context(f'Error processing Audit Checksheet form1: {e}', level=logging.ERROR)
            transaction.rollback()
            return JsonResponse({'status': 'error', 'message': message}, status=500)

        except Exception as e:
            message = str(e)
            log_with_context(f'Error processing Audit Checksheet form2: {message}', level=logging.ERROR)
            log_with_context("Rolling back transaction due to unexpected error", level=logging.ERROR)
            transaction.rollback()
            return JsonResponse({'status': 'error', 'message': message}, status=500)

    else:
        log_with_context('Audit Checksheet form not received from client', level=logging.ERROR)
        return JsonResponse({'status': 'error', 'message': 'Form not received'}, status=405)

@csrf_exempt
def opn_audit_checksheet(request):
    global audit_comment, rework_comment
    audit_comment = []
    rework_comment = []
    if request.method == 'POST':
        data = json.loads(request.body)
        esn = int(data['esn'])
        stno = int(data['stno'])
        result_dict = egn_status(esn, stno)
        cur_loct = get_object_or_404(Locations, loc_id=int(stno))
        result_loct = cur_loct.result_field
        result_id = f"{esn}_{result_loct}"

        rslt_header = EngResultHeader.objects.filter(result_id=result_id).select_related('bom_srno').values(
            'result_id',
            'esn',
            'stno',
            'timestamp',
            'emp_id',
            'username',
            'remark',
            'bom_srno__model',
            'bom_srno__description',
            'bom_srno__series'
        )

        eng_checkpoints = EngResultCheckpoints.objects.filter(result_id=result_id).select_related(
            'checkpoint').values('result_id', 'checkpoint_status','seq_no' , 'checkpoint__checkpoint_id',
                                 'checkpoint__checkpoint')

        rslt_image = EngResultImages.objects.filter(result_id = result_id).values( 'image_id', 'directory')
        rslt_image_list = list(rslt_image.values())
        # Get list of Images
        base64_images = []
        for item in rslt_image_list:
            # Remove slashes from date
            image_id = re.sub(r'/', '', item['image_id'])
            image_id = re.sub(r':', '', image_id)

            # Check for .jpeg or .png extension
            possible_extensions = ['.jpeg', '.png']
            image_data = None

            for ext in possible_extensions:
                image_filename = image_id + ext
                image_path = os.path.join(os.getcwd(), 'Images', item['directory'], image_filename)

                if os.path.exists(image_path):
                    with open(image_path, "rb") as image_file:
                        image_data = image_file.read()
                    break

            if image_data:
                base64_image = base64.b64encode(image_data).decode('utf-8')
                base64_images.append(base64_image)
            else:
                print(f"Image {image_id} with extensions {possible_extensions} not found.")


        if result_dict['fail_status'] == True :
            rework_comment = EngResultRework.objects.filter(result_id=result_id).values('esn', 'stno', 'timestamp',
                                                                                      'emp_id', 'username', 'remark')
            result_id = f"{esn}_{result_loct}_0"
            audit_comment = EngResultAudit.objects.filter(result_id=result_id).values('esn', 'stno', 'timestamp',
                                                                                      'emp_id', 'username', 'remark')

        # Construct response data
        response_data = {
            'status': 'success',
            'message': 'Engine Result to open.',
            'header_data': list(rslt_header),
            'checkpoint_data': list(eng_checkpoints),
            'images': base64_images,
            'audit_comment' : list(audit_comment),
            'rework_comment' : list(rework_comment),
            'rework_status' : result_dict['fail_status']
        }

        return JsonResponse(response_data)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def audit_checksheet(request):
    if request.method == 'POST':
        try:
            log_with_context("Starting transaction", level=logging.INFO)

            # Log the size of the raw request body
            raw_request_body = request.body
            request_body_size = len(raw_request_body)
            log_with_context(f'Size of raw request body: {request_body_size} bytes', level=logging.INFO)

            # Parse request body JSON
            data = json.loads(request.body)
            parsed_data_size = len(json.dumps(data))
            log_with_context(f'Size of parsed request data: {parsed_data_size} bytes', level=logging.INFO)
            stno = data.get('stno', '')
            esn = data.get('esn', '')
            emp_id = data.get('userId', '')
            remark = data.get('remark', '')
            username = data.get('userName', '')
            currentTime = data.get('currentTime', '')
            audit_rslt = data.get('result', '')
            result_id = f"{esn}_{stno}_0"
            if audit_rslt == 'ReCheck':
                result_id = f"{esn}_{stno}_1"

                # Check if the checksheet already existed
                if EngResultAudit.objects.filter(result_id=result_id).exists():
                    log_with_context(f'checksheet already submitted  for ESN {esn} at STNO {stno}', level=logging.INFO)
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Checksheet for Engine: {esn} at station: {stno} already submitted'
                    })

            with transaction.atomic():
                # Log receipt of Checksheet form
                log_with_context(f'Received Audit Checksheet form from client for {esn} at {stno}', level=logging.INFO)
                header_instance = EngResultAudit(
                    result_id=result_id,
                    esn=esn,
                    stno=int(stno),
                    timestamp=currentTime,
                    emp_id=emp_id,
                    username=username,
                    remark=remark,
                )
                header_instance.save()
                log_with_context(f"Audit Check data for result ID {result_id} stored in DB.", level=logging.INFO)

                eng = get_object_or_404(EngLocation, esn = esn)
                location = eng.cur_loc
                cur_loct = get_object_or_404(Locations, loc_id=int(stno))
                pass_loct = cur_loct.pass_field
                fail_loct = cur_loct.fail
                if audit_rslt == 'Pass':
                        field_name1 = f"st{pass_loct}_status"
                        field_value1 = True  # Example value
                        field_name2 = f"st{pass_loct}_date"
                        field_value2 = timezone.now()
                        field_name3 = "cur_loc"
                        field_value3 = int(pass_loct)

                        update_eng_location(esn, field_name1, field_value1, field_name2, field_value2, field_name3,
                                                field_value3)
                if audit_rslt == 'Fail':
                        field_name1 = f"st{fail_loct}_status"
                        field_value1 = True  # Example value
                        field_name2 = f"st{fail_loct}_date"
                        field_value2 = timezone.now()
                        field_name3 = "cur_loc"
                        field_value3 = int(fail_loct)
                        field_name4 = f"st{location}_status"
                        field_value4 = False
                        update_eng_location_fail(esn, field_name1, field_value1, field_name2, field_value2, field_name3,
                                                field_value3, field_name4, field_value4)
                if audit_rslt == 'ReCheck':
                        field_name1 = f"st{pass_loct}_status"
                        field_value1 = True  # Example value
                        field_name2 = f"st{pass_loct}_date"
                        field_value2 = timezone.now()
                        field_name3 = "cur_loc"
                        field_value3 = int(pass_loct)

                        update_eng_location(esn, field_name1, field_value1, field_name2, field_value2, field_name3,
                                                field_value3)


            return JsonResponse({'status': 'success', 'message': 'Form submitted and data saved.'})

        except IntegrityError as e:
            message = str(e)
            log_with_context(f'Error processing Audit Checksheet form1: {e}', level=logging.ERROR)
            transaction.rollback()
            return JsonResponse({'status': 'error', 'message': message}, status=500)

        except Exception as e:
            message = str(e)
            log_with_context(f'Error processing Audit Checksheet form2: {message}', level=logging.ERROR)
            log_with_context("Rolling back transaction due to unexpected error", level=logging.ERROR)
            transaction.rollback()
            return JsonResponse({'status': 'error', 'message': message}, status=500)

    else:
        log_with_context('Audit Checksheet form not received from client', level=logging.ERROR)
        return JsonResponse({'status': 'error', 'message': 'Form not received'}, status=405)

@csrf_exempt
def engine_checksheet_result(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        esn = data['esn_r']
        stno = data['stno_r']
        result_id = f"{esn}_{stno}"

        rslt_header = EngResultHeader.objects.filter(result_id=result_id).select_related('bom_srno').values(
            'result_id',
            'esn',
            'stno',
            'timestamp',
            'emp_id',
            'username',
            'remark',
            'bom_srno__bom',
            'bom_srno__model',
            'bom_srno__description',
            'bom_srno__series'
        )

        eng_checkpoints = EngResultCheckpoints.objects.filter(result_id=result_id).select_related(
            'checkpoint').values('result_id', 'checkpoint_status','seq_no' , 'checkpoint__checkpoint_id',
                                 'checkpoint__checkpoint')

        rslt_image = EngResultImages.objects.filter(result_id = result_id).values( 'image_id', 'directory')
        rslt_image_list = list(rslt_image.values())
        # Get list of Images
        base64_images = []
        for item in rslt_image_list:
            # Remove slashes from date
            image_id = re.sub(r'/', '', item['image_id'])
            image_id = re.sub(r':', '', image_id)

            # Check for .jpeg or .png extension
            possible_extensions = ['.jpeg', '.png']
            image_data = None

            for ext in possible_extensions:
                image_filename = image_id + ext
                image_path = os.path.join(os.getcwd(), 'Images', item['directory'], image_filename)

                if os.path.exists(image_path):
                    with open(image_path, "rb") as image_file:
                        image_data = image_file.read()
                    break

            if image_data:
                base64_image = base64.b64encode(image_data).decode('utf-8')
                base64_images.append(base64_image)
            else:
                print(f"Image {image_id} with extensions {possible_extensions} not found.")


        # Construct response data
        response_data = {
            'status': 'success',
            'message': 'Engine Result to open.',
            'header_data': list(rslt_header),
            'checkpoint_data': list(eng_checkpoints),
            'images': base64_images
        }

        return JsonResponse(response_data)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


#  Related Database connections
@csrf_exempt
def database_connection(request):
    table_data = {}
    if request.method == 'POST':
        data = json.loads(request.body)
        table_name = data['dropdownValue']
        # Define a mapping between dropdown values and model classes
        model_mapping = {
            'checkpoint_list': EngCheckpoint,
            'map_checkpoint': CheckpointMap,
            'engmodel_list': EngModel,
            'bom_list': BomList,
        }
        # Get the model class based on the dropdown value
        table_model = model_mapping.get(table_name)
        if table_model:
            table_data = list(table_model.objects.values())
            status = 'success'
            message = 'Database is uploaded'
        else:
            status = 'error'
            message = 'Invalid table name'

        # Construct response data
        response_data = {
            'status': status,
            'message': message,
            'table_data': table_data,
        }

        return JsonResponse(response_data)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def data_delete(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        table_name = data['data']['dropdownValue']
        first_key, id = next(iter(data['data']['rowdata'].items()))
        # # Define a mapping between dropdown values and model classes
        model_mapping = {
            'checkpoint_list': EngCheckpoint,
            'map_checkpoint': CheckpointMap,
            'bom_list': BomList,
            'engmodel_list': EngModel,
        }
        # # Get the model class based on the dropdown value
        table_model = model_mapping.get(table_name)
        if table_model:
            # Fetch data from the selected model
            filter_kwargs = {first_key: id}
            table_data = table_model.objects.filter(**filter_kwargs)
            # Delete the fetched data
            try:
                # Attempt to delete the data
                table_data.delete()
                status = 'success'
                message = f"Deleted the row {id}"
            except Exception as e:
                # Handle deletion errors
                status = 'error'
                message = f"Error deleting entry with ID {id}: {str(e)}"
            finally:
                print(message)
        else:
            status = 'error'
            message = 'Invalid table name or row Id'

        response_data = {
            'status': status,
            'message': message,
        }

        return JsonResponse(response_data)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def data_edit(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # row_id = next(iter(data['data']['rowdata'].items()))
        table_name = data['data']['dropdownValue']
        first_key, id = next(iter(data['data']['rowdata'].items()))
        # Define a mapping between dropdown values and model classes
        model_mapping = {
            'checkpoint_list': EngCheckpoint,
            'map_checkpoint': CheckpointMap,
            'bom_list': BomList,
            'engmodel_list': EngModel,
        }
        # Get the model class based on the dropdown value
        table_model = model_mapping.get(table_name)
        if table_model:
            # Fetch data from the selected model
            filter_kwargs = {first_key: id}
            table_data = list(table_model.objects.filter(**filter_kwargs).values())
            #  add code to delete the data
            status = 'success'
            message = f"Deleted the row {id}"
        else:
            status = 'error'
            message = 'Invalid table name or row Id'
        response_data = {
            'status': status,
            'message': message,
        }

        return JsonResponse(response_data)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def data_new_entry(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        table_name = data.get('dropdownValue')

        # Define a mapping of table names to serializers
        serializer_mapping = {
            'checkpoint_list': EngCheckpointSerializer,
            'map_checkpoint': CheckpointMapSerializer,
            'bom_list': BomListSerializer,
            'engmodel_list': EngmodelSerializer,
        }
        serializer_class = serializer_mapping.get(table_name)
        if serializer_class:
            serializer = serializer_class()
            # Get the fields of the serializer
            fields_info = []
            max_length = 10

            for field_name, field in serializer.fields.items():
                # Determine the type of the field
                field_type = None
                choices = None

                if isinstance(field, serializers.IntegerField):
                    field_type = 'integer'
                elif isinstance(field, serializers.DateTimeField):
                    field_type = 'datetime'
                elif isinstance(field, serializers.BooleanField):
                    field_type = 'boolean'
                elif isinstance(field, serializers.PrimaryKeyRelatedField):
                    field_type = 'foreignkey'
                    related_model = field.queryset.model
                    choices = list(related_model.objects.all().values_list('pk', flat=True))
                elif isinstance(field, serializers.SlugRelatedField):
                    field_type = 'foreignkey'
                    related_model = field.queryset.model
                    choices = list(related_model.objects.all().values_list(field.slug_field, flat=True))
                elif isinstance(field, serializers.CharField):
                    field_type = 'text'
                    max_length = getattr(field, 'max_length', None)
                try:
                    if hasattr(field, 'choices'):
                        choices = field.choices
                except:
                    pass

                # Get the help_text for the field
                help_text = getattr(serializer.Meta.model, field_name).field.help_text if hasattr(serializer.Meta.model, field_name) else None

                # Add field name, type, help_text, and choices to fields_info list
                fields_info.append({
                    'name': field_name,
                    'type': field_type,
                    'help_text': help_text,
                    'choices': choices,
                    'max_length': max_length
                })

            return JsonResponse({'status': 'success', 'fields': fields_info, 'table_name': table_name})
        else:
            return JsonResponse({'status': 'error', 'message': 'Serializer not found'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

@csrf_exempt
def save_new_entry(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            formdata = data['formData']
            tablename = data['formTable']
            model_mapping = {
                'bom_list': BomList,
                'engmodel_list': EngModel,
                'checkpoint_list': EngCheckpoint,
                'map_checkpoint': CheckpointMap,
            }
            modelname = model_mapping.get(tablename['tablename'])
            fields = {}
            for key, value in formdata.items():
                if hasattr(modelname, key):
                    # If the value is empty, replace it with None
                    fields[key] = value if value else None

                    if tablename['tablename'] == 'map_checkpoint' and key == 'stno':
                        value1 = Operation.objects.get(op_name=value).stno
                        fields['stno'] = Operation.objects.get(pk=value1)

                    if tablename['tablename'] == 'map_checkpoint' and key == 'bom':
                        fields['bom'] = BomList.objects.get(pk=value)

                    if tablename['tablename'] == 'map_checkpoint' and key == 'checkpoint':
                        fields['checkpoint'] = EngCheckpoint.objects.get(pk=value)

                    if tablename['tablename'] == 'map_checkpoint' and key == 'map_status':
                        fields['map_status'] = fields['map_status'].lower() == 'on'

            new_entry = modelname.objects.create(**fields)
            return JsonResponse({'status': 'success'})
        except IntegrityError as e:
            # Return an error response if IntegrityError occurs
            return JsonResponse({'status': 'error', 'message': str(e)})
        except Exception as e:
            # Return an error response for other exceptions
            return JsonResponse({'status': 'error', 'message': str(e)})

# Data entry for stno 10
@csrf_exempt
def opn_ops_st10(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        esn = int(data['esn'])
        stno = int(data['stno'])

        try:
            checkdata = EngineAsslyOp.objects.get(esn=esn)
            global hold_remark, hold_status, operator_h_id, timestamp_h, hold_crankcase_no, hold_fip_no, hold_turbo_no
            hold_remark = checkdata.hold_remark
            hold_status = checkdata.hold_status
            operator_h_id = checkdata.operator_h_id
            timestamp_h = checkdata.timestamp_h
            hold_crankcase_no = checkdata.crankcase_no
            hold_fip_no = checkdata.fip_no
            hold_turbo_no = checkdata.turbo_no
        except EngineAsslyOp.DoesNotExist:
            # If the record does not exist, initialize variables to default values or handle appropriately
            hold_remark, hold_status, operator_h_id, timestamp_h, hold_crankcase_no, hold_fip_no, hold_turbo_no = None, None, None, None, None, None, None
            logger.warning(f"No EngineAsslyOp record found for ESN {esn}")
        except Exception as e:
            logger.error(f"Unexpected error retrieving EngineAsslyOp record for ESN {esn}: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

        try:
            result_dict = egn_status(esn, stno)  # get detail of next & previous station as per current station
            eng = EngLocation.objects.get(esn=esn)  # get engine detail from table Englocation
            bom_detail = get_object_or_404(BomList, bom=eng.bom)  # get respective engine detail as per bom
            bom, model, type, series, description = bom_detail.bom, bom_detail.model, bom_detail.type, bom_detail.series, bom_detail.description

            cur_loct = get_object_or_404(Locations, loc_id=int(stno))  # get detail of current location detail
            pass_loct, fail_loct, result_loct, activity = cur_loct.pass_field, cur_loct.fail, cur_loct.result_field, cur_loct.activity
            result_id = f"{esn}_{result_loct}"
            logger.info(f'Location status for ESN {esn}: {stno}')

        except EngLocation.DoesNotExist:
            logger.info(f'Engine {esn} is not found in records')
            return JsonResponse({
                'status': 'error',
                'message': f'Engine {esn} is not found in records'
            })
        except Exception as e:
            logger.error(f"Unexpected error processing data for ESN {esn}: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

        pass_location = get_object_or_404(Locations, loc_id=pass_loct).location_desc
        fail_location = '--Na--'

        if fail_loct != 0:
            fail_location = get_object_or_404(Locations, loc_id=fail_loct).location_desc
        result_location = get_object_or_404(Locations, loc_id=result_loct).location_desc

        header_data = {
            'esn': esn,
            'engmodel': model,
            'stno': result_loct,
            'bom': bom,
            'type': type,
            'series': series,
            'description': description,
            'pass_loc': pass_location,
            'fail_loc': fail_location,
            'result_loc': result_location,
            'activity': activity,
            'hold_remark': hold_remark,
            'hold_status': hold_status,
            'operator_h_id': operator_h_id,
            'timestamp_h': timestamp_h,
            'cranckcase_no': hold_crankcase_no,
            'fip_no' : hold_fip_no,
            'turbo_no': hold_turbo_no

        }

        logger.info(f'St10 operator input is open')

        return JsonResponse({
            'status': 'success',
            'header_data': header_data,
            'message': 'Checksheet form data sent'
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
def assemblyop_submit(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            esn = data.get('esn')
            crank_case_no = data.get('crankCaseNo')
            fip_no = data.get('fipNo')
            turbo_no = data.get('turboNo')
            remark = data.get('remark')
            user_id = data.get('userId')
            datetime_str = data.get('currentTimeStamp')
            input_format = "%m/%d/%Y, %I:%M:%S %p"
            timestamp = datetime.strptime(datetime_str, input_format)
            status = data.get('status')
            hold_remark = data.get('holdRemark')
            hold_status = data.get('holdStatus')


            # Fetch EngLocation and associated BomList instance
            esn_instance = get_object_or_404(EngLocation, esn=esn)
            bom_instance = get_object_or_404(BomList, bom=esn_instance.bom)

            with transaction.atomic():
                try:
                    if hold_status:  # Check if hold_status is True
                        # Update existing entry
                        engine_detail = EngineAsslyOp.objects.filter(esn=esn).update(
                            crankcase_no=crank_case_no,
                            fip_no=fip_no,
                            turbo_no=turbo_no,
                            remark=remark,
                            operator_id=user_id,
                            timestamp=timestamp,
                            hold_status=False,  # Set hold_status to False
                            status = True
                        )
                    else:
                        # Save new data to the database
                        engine_detail = EngineAsslyOp(
                            esn=esn,
                            crankcase_no=crank_case_no,
                            fip_no=fip_no,
                            turbo_no=turbo_no,
                            remark=remark,
                            operator_id=user_id,
                            timestamp=timestamp,
                            bom=bom_instance,
                            status=status,
                            hold_remark=hold_remark,
                            hold_status=hold_status
                        )
                        engine_detail.save()

                    # Update EngLocation
                    field_name1 = f"st10_status"
                    field_value1 = True
                    field_name2 = f"st10_date"
                    field_value2 = timezone.now()
                    field_name3 = "cur_loc"
                    field_value3 = 30

                    update_eng_location(esn, field_name1, field_value1, field_name2, field_value2, field_name3, field_value3)

                except Exception as e:
                    print("Error saving EngineAsslyOp:", e)
                    return JsonResponse({'error': 'Failed to save engine detail'}, status=500)

                return JsonResponse({'status': 'success'}, status=200)
        except json.JSONDecodeError:
            print("Error decoding JSON")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print("General error:", e)
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def assemblyop_hold(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            esn = data.get('esn')
            hold_remark = data.get('holdRemark')
            hold_status = data.get('holdStatus')
            user_id = data.get('userId')
            datetime_str = data.get('currentTimeStamp')
            crankcase_no = data.get('crankCaseNo')
            fip_no = data.get('fipNo')
            turbo_no = data.get('turboNo')
            remark = data.get('remark')
            status = data.get('status')
            input_format = "%m/%d/%Y, %I:%M:%S %p"
            timestamp = datetime.strptime(datetime_str, input_format)
            logger.info(f"Received data: {data}")

            # Fetch EngLocation and associated BomList instance
            esn_instance = get_object_or_404(EngLocation, esn=esn)
            bom_instance = get_object_or_404(BomList, bom=esn_instance.bom)

            with transaction.atomic():
                try:
                    engine_detail = EngineAsslyOp(
                        esn=esn,
                        bom=bom_instance,  # Pass the BomList instance
                        operator_h_id=user_id,
                        timestamp_h=timestamp,
                        hold_remark=hold_remark,  # Save hold remark
                        hold_status=hold_status,  # Save hold status
                        crankcase_no=crankcase_no,
                        fip_no=fip_no,
                        turbo_no=turbo_no,
                        remark=remark,
                        status = status,
                    )

                    engine_detail.save()

                    # Update EngLocation with new status and other fields
                    field_name1 = f"st12_status"
                    field_value1 = True  # Example value
                    field_name2 = f"st12_date"
                    field_value2 = timezone.now()
                    field_name3 = "cur_loc"
                    field_value3 = 12
                    field_name4 = f"st10_status"
                    field_value4 = False
                    update_eng_location_fail(esn, field_name1, field_value1, field_name2, field_value2, field_name3,
                                             field_value3, field_name4, field_value4)

                    logger.info("Database update successful")

                except Exception as e:
                    print("Error saving EngineAsslyOp:", e)
                    return JsonResponse({'error': 'Failed to save engine detail'}, status=500)

            return JsonResponse({'status': 'success'}, status=200)
        except json.JSONDecodeError:
            print("Error decoding JSON")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print("General error:", e)
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == 'GET':
        esn = request.GET.get('esn')
        if not esn:
            return JsonResponse({'error': 'ESN parameter is required'}, status=400)

        try:
            engine_details = EngineAsslyOp.objects.filter(esn=esn).values(
                'esn', 'hold_remark', 'hold_status', 'operator_h_id', 'timestamp_h'
            )

            if not engine_details:
                return JsonResponse({'error': 'No data found for the given ESN'}, status=404)

            return JsonResponse({'data': list(engine_details)}, status=200)

        except Exception as e:
            print("Error retrieving data:", e)
            return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def get_assemblyop_result(request):
    response_data = {'status': 'error', 'message': 'An unknown error occurred'}

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            esn = data.get('esn_r')
            stno = data.get('stno_r')

            try:
                eng = EngLocation.objects.get(esn=esn)
            except EngLocation.DoesNotExist:
                response_data['message'] = f'No engine found for ESN: {esn}'
                return JsonResponse(response_data, status=404)

            bom_detail = get_object_or_404(BomList, bom=eng.bom)
            bom, model, type, series, description = bom_detail.bom, bom_detail.model, bom_detail.type, bom_detail.series, bom_detail.description

            cur_loct = get_object_or_404(Locations, loc_id=int(stno))
            pass_loct, fail_loct, result_loct, activity = cur_loct.pass_field, cur_loct.fail, cur_loct.result_field, cur_loct.activity

            # Query the database for matching records
            data = list(EngineAsslyOp.objects.filter(esn=esn).values())

            pass_location = get_object_or_404(Locations, loc_id=pass_loct).location_desc
            fail_location = '--Na--'
            if fail_loct != 0:
                fail_location = get_object_or_404(Locations, loc_id=fail_loct).location_desc
            result_location = get_object_or_404(Locations, loc_id=result_loct).location_desc

            hold_remark = None
            if int(stno) == 10 and data:
                hold_remark = data[0].get('hold_remark')

            header_data = {
                'esn': esn,
                'engmodel': model,
                'stno': stno,
                'bom': bom,
                'type': type,
                'series': series,
                'description': description
            }

            # Ensure the time_stamp is included
            if data:
                response_data = {
                    'status': 'success',
                    'message': f'Table exported for station number {stno}',
                    'data': data,
                    'header_data': header_data,
                    'pass_loc': pass_location,
                    'fail_loc': fail_location,
                    'result_loc': result_location,
                    'activity': activity,
                    'hold_remark': hold_remark
                }
                print(response_data)
            else:
                response_data = {
                    'message': f'No data found for ESN: {esn}'
                }


        except json.JSONDecodeError:
            logger.error("Invalid JSON input")
            response_data['message'] = "Invalid JSON input"
        except Exception as e:
            logger.error(f"Error fetching GetAssemblyOpResult data: {e}", exc_info=True)
            response_data['message'] = 'An error occurred while fetching data'

    return JsonResponse(response_data, status=200)





# def get_assemblyop_result(request):
#     response_data = {'status': 'error', 'message': 'An unknown error occurred'}
#
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             esn = data.get('esn_r')
#             stno = data.get('stno_r')
#
#             try:
#                 eng = EngLocation.objects.get(esn=esn)  # get engine detail from table Englocation
#             except EngLocation.DoesNotExist:
#                 response_data['message'] = f'No engine found for ESN: {esn}'
#                 return JsonResponse(response_data, status=404)
#
#             bom_detail = get_object_or_404(BomList, bom=eng.bom)  # get respective engine detial as per bom
#             # get all detail from table bom
#             bom, model, type, series, description = bom_detail.bom, bom_detail.model, bom_detail.type, bom_detail.series, bom_detail.description
#
#             cur_loct = get_object_or_404(Locations, loc_id=int(stno))  # get detail of current location detail
#             # get all detail of next, previous & resulted stations
#             pass_loct, fail_loct, result_loct, activity = cur_loct.pass_field, cur_loct.fail, cur_loct.result_field, cur_loct.activity
#
#             # Query the database for matching records
#             data = list(EngineAsslyOp.objects.filter(esn=esn).values())
#             pass_location = get_object_or_404(Locations, loc_id=pass_loct).location_desc
#             fail_location = '--Na--'
#             if fail_loct != 0:
#                 fail_location = get_object_or_404(Locations, loc_id=fail_loct).location_desc
#             result_location = get_object_or_404(Locations, loc_id=result_loct).location_desc
#
#             # Include hold remark if station is 10
#             hold_remark = None
#             if int(stno) == 10 and data:
#                 hold_remark = data[0].get('hold_remark')
#             header_data = {
#                 'esn': esn,
#                 'engmodel': model,
#                 'stno': stno,
#                 'bom': bom,
#                 'type': type,
#                 'series': series,
#                 'description': description
#             }
#             # Ensure only the first item is returned
#             if data:
#                 response_data = {
#                     'status': 'success',
#                     'message': f'Table exported for station number {stno}',
#                     'data': data,
#                     'header_data' : header_data,
#                     'pass_loc': pass_location,
#                     'fail_loc': fail_location,
#                     'result_loc': result_location,
#                     'activity': activity,
#                     'hold_remark': hold_remark
#                 }
#             else:
#                 response_data= {
#                     'message' : f'No data found for ESN: {esn}'}
#
#         except json.JSONDecodeError:
#             logger.error("Invalid JSON input")
#             response_data['message'] = "Invalid JSON input"
#         except Exception as e:
#             logger.error(f"Error fetching GetAssemblyOpResult data: {e}", exc_info=True)
#             response_data['message'] = 'An error occurred while fetching data'
#
#     return JsonResponse(response_data, status=200)
