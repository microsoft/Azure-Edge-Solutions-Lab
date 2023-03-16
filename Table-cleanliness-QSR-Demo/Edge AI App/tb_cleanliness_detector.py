import pyds
import requests
import json
import time
from datetime import datetime, timezone, timedelta
ol_t_threshold = 120
lv_t_threshold = 300

ROUTE = 'inference'
SVC = 'http://contoso-webapp-service'
PORT = '5000' 
URL = f'{SVC}:{PORT}/{ROUTE}'

class Table:
    def __init__(self, bbox, object_id, cleanliness):
        self.id = object_id
        self.bbox = bbox
        self.overlapped = False
        self.cleanliness = cleanliness


def cal_rect_params(rect_params):
    
    top, left, width, height = int(rect_params.top), int(rect_params.left), int(rect_params.width), int(rect_params.height)
    x_start, y_start, x_end, y_end = left, top, left + width, top + height

    return x_start, y_start, x_end, y_end  


def overlapped(tb_bbox, p_bbox):
    x_tb_start, y_tb_start, x_tb_end, y_tb_end = tb_bbox
    x_p_start, y_p_start, x_p_end, y_p_end = p_bbox
 
    if max(x_tb_start, x_p_start) < min(x_tb_end, x_p_end) and max(y_tb_start, y_p_start) < min(y_tb_end, y_p_end):
        return True    
    return False

def overlapped_area_cal(tb_bbox, p_bbox):
    x_tb_start, y_tb_start, x_tb_end, y_tb_end = tb_bbox
    x_p_start, y_p_start, x_p_end, y_p_end = p_bbox  
    
    area = (min(x_tb_end, x_p_end) - max(x_tb_start, x_p_start)) * (min(y_tb_end, y_p_end) * max(y_tb_start, y_p_start))

    return area

def inter_communi_pods(tb_dict, tb_to_counter, now):
    for tb_object_id, table in tb_dict.items():
        table_id = table.id  
        cleanliness = table.cleanliness
        occupancy = tb_to_counter[table_id]['occupancy']
        status =  tb_to_counter[table_id]['status']
        timestamp = now
        headers = {'Content-Type': 'application/json'}

        try:
            print(f'post request: table_id: {str(table_id)}, occupancy: {occupancy}, cleanliness: {cleanliness}, status: {status}, timestamp: {now}')
            #print(URL)
            #resp = requests.post(URL, headers=headers, json={"id": "table_cleanliness", "table_id": str(table_id), "state": status, "timestamp": now)
            #print(f'http response status: {resp.ok}')
            #time.sleep(1)
        
        except Exception as e: 
            print(e)


def tb_cleanliness_detector(obj_counter, l_obj, tbid_to_counter):
    ppl_bboxes = []
    tb_dict = {}
    now = datetime.now()

    while l_obj is not None:
        try:
            # Casting l_obj.data to pyds.NvDsObjectMeta
            obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
            obj_counter[obj_meta.class_id] += 1
            rect_params = obj_meta.rect_params
            x_start, y_start, x_end, y_end = cal_rect_params(rect_params)
            
            # SAVE OBJ_METADATA
            if obj_meta.obj_label == 'people':
                ppl_bboxes.append((x_start, y_start, x_end, y_end))
                # print(ppl_bboxes)

            # print(f'obj_meta.object_id: {obj_meta.object_id}, obj_meta.obj_label: {obj_meta.obj_label}, obj_meta.confidence: {obj_meta.confidence}, bbox = ({x_start}, {y_start}), ({x_end}, {y_end})')
            c_obj = obj_meta.classifier_meta_list

            while c_obj is not None:
                
                try:
                    cls_meta = pyds.NvDsClassifierMeta.cast(c_obj.data)
                    label_obj = cls_meta.label_info_list
                    while label_obj is not None:
                        try:
                            label_meta = pyds.NvDsLabelInfo.cast(label_obj.data)                            
                            # ===== init table class ====
                            if label_meta.result_label != 'clean':
                                tb_dict[obj_meta.object_id] = Table((x_start, y_start, x_end, y_end), obj_meta.object_id, False)
                            else: 
                                tb_dict[obj_meta.object_id] = Table((x_start, y_start, x_end, y_end), obj_meta.object_id, True)

                            label_obj=label_obj.next
                        except StopIteration:
                            break
                        
                    c_obj=c_obj.next

                except StopIteration:
                    break


        except StopIteration:
            break

        
        
        try:              
            l_obj = l_obj.next
        except StopIteration:
            break
        
        # ===== Check overlap of the table and assign overlapped value to tb class======
        for ppl_bbox in ppl_bboxes:
            overlapped_area = 0 
            max_overlapped_area = 0
            max_area_tb_id = -1

            for tb_object_id, table in tb_dict.items():
                if not overlapped(table.bbox, ppl_bbox):
                    continue

                overlapped_area = overlapped_area_cal(table.bbox, ppl_bbox)
                if overlapped_area > max_overlapped_area:
                    max_overlapped_area = overlapped_area
                    max_area_tb_id = tb_object_id

            # Update the overlapped field of the table to True if the bounding box of the table has the maximum overlapped area with the bounding box of the person
            if max_area_tb_id >= 0: 
                tb_dict[max_area_tb_id].overlapped = True
 

    for tb_object_id, table in tb_dict.items():
        table_state = tbid_to_counter[tb_object_id]
        if table.overlapped:
            table_state['counter'] += 1
        
        else:
            table_state['counter'] = 0
            if table_state['last_overlapped_ts']:
                delta = now - table_state['last_overlapped_ts']
                if delta >  timedelta(seconds=lv_t_threshold):
                    print(f"table {tb_object_id} becomes unoccupied")
                    table_state['occupancy'] = False
                    if table.cleanliness:
                        table_state['status'] = 'Clean'
                    else:
                        table_state['status'] = 'Need_clean'

    
        if table_state['counter'] >= ol_t_threshold: # more than three sec
            print("======occupied======")
            table_state['occupancy'] = True
            table_state['status'] = 'Occupied'
            table_state['last_overlapped_ts'] = now
    
    inter_communi_pods(tb_dict, tbid_to_counter, now)

