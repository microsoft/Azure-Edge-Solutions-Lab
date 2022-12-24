import pyds
import requests
import json
import time

MIN_BAG_NUM = 2
BAG_LEFT_DEFAULT_BBOX = (649, 444, 946, 901)
BAG_RIGHT_DEFAULT_BBOX = (917, 416, 1223, 910)
DIST_THRESH = 4 
MIN_FRAME_LEN = 3 
BAG_MIN_OVERLAP_PERC = 0.45
BAG_MAX_OVERLAP_PERC = 0.9 
ITEM_CONF_THRESH = 0.5
ROUTE = 'post_items_placement'
SVC = 'http://contoso-webapp-service'
PORT = '5000' 
URL = f'{SVC}:{PORT}/{ROUTE}'

class Bag:
    def __init__(self, bbox):
        self.bbox = bbox

class Item:
    def __init__(self, object_id, label_name):
        self.object_id = object_id
        self.label_name = label_name
        self.past_frame_y_start = []


def get_bag_dict(bag_preds_rect):
    # init
    bag_left = Bag((0, 0, 0, 0))
    bag_right = Bag((0, 0, 0, 0)) 

    if len(bag_preds_rect) != MIN_BAG_NUM:
        bag_left.bbox = BAG_LEFT_DEFAULT_BBOX
        bag_right.bbox = BAG_RIGHT_DEFAULT_BBOX

        return bag_left, bag_right
    
    bag_preds_rect = sorted(bag_preds_rect)
    bag_left.bbox = bag_preds_rect[0]
    bag_right.bbox = bag_preds_rect[1]

    return bag_left, bag_right


def overlapped(bag_bbox, item_bbox):
    x_bag_start, y_bag_start, x_bag_end, y_bag_end = bag_bbox
    start_point, end_point = item_bbox
    x_item_start, y_item_start = start_point
    x_item_end, y_item_end = end_point

    w = min(x_bag_end, x_item_end) - max(x_bag_start, x_item_start)
    h = min(y_bag_end, y_item_end) - max(y_bag_start, y_item_start)

    width = x_item_end - x_item_start  
    height = y_item_end - y_item_start 
    item_area =  width * height

    if w > 0 and h > 0:
        return w * h/ item_area
    
    return 0
    

def items_movement_to_action(item_dict, item):
    action = ''
    obj_label = item.obj_label
    object_id = item.object_id

    if len(item_dict[object_id].past_frame_y_start) < MIN_FRAME_LEN:
        action = 'add'
        return action
    
    action = 'drifted'

    for last in range(MIN_FRAME_LEN - 1):
        new = item_dict[object_id].past_frame_y_start[-1 - last]
        old = item_dict[object_id].past_frame_y_start[-2 - last]
        
        if not new > old + DIST_THRESH :
            break
    
    else:
        action = 'add'
    
    for last in range(MIN_FRAME_LEN - 1):
        new = item_dict[object_id].past_frame_y_start[-1 - last]
        old = item_dict[object_id].past_frame_y_start[-2 - last]
        
        if not new < old - DIST_THRESH :
            break
    
    else:
        action = 'remove'
    
    return action


def inter_communi_pods(bag_no, item_dict, item, action_set):
    action = items_movement_to_action(item_dict, item)
    
    if action == 'drifted' or item.obj_label == 'bag':
        return

    if (item.object_id, action) not in action_set:
        action_set.add((item.object_id, action))

        headers = {'Content-Type': 'application/json'}

        try:
            print(f'post request: bag_no: {str(bag_no)}, item_name: {item.obj_label}, action: {action}')
            resp = requests.post(URL, headers=headers, json={'bag_no': bag_no, 'item_name': item.obj_label, 'action': action })
            print(f'http response status: {resp.ok}')
            time.sleep(1)
        
        except Exception as e: 
            print(e)

def cal_rect_params(rect_params):
    
    top, left, width, height = int(rect_params.top), int(rect_params.left), int(rect_params.width), int(rect_params.height)
    x_start, y_start, x_end, y_end = left, top, left + width, top + height

    return x_start, y_start, x_end, y_end        

def items_tracking(item_dict, frame_number, l_obj, left_action_set, right_action_set):
    bag_preds_rect = []
    item_preds = []

    
    while l_obj is not None:
        try:
            # Casting l_obj.data to pyds.NvDsObjectMeta
            obj_meta=pyds.NvDsObjectMeta.cast(l_obj.data)
        
        except StopIteration:
            break
        
        rect_params = obj_meta.rect_params
        x_start, y_start, x_end, y_end = cal_rect_params(rect_params)
        
        if obj_meta.obj_label == 'bag':
            bag_preds_rect.append((x_start, y_start, x_end, y_end))
        
        else:
            item_preds.append(obj_meta)
            
            if obj_meta.object_id not in item_dict:
                item_dict[obj_meta.object_id] = Item(obj_meta.object_id, obj_meta.obj_label)

            item_dict[obj_meta.object_id].past_frame_y_start.append(y_start)

        try: 
            l_obj=l_obj.next

        except StopIteration:
            break
    
    bag_left, bag_right = get_bag_dict(bag_preds_rect)
    
    for item in item_preds:
        
        if item.confidence < ITEM_CONF_THRESH:
            continue
        
        rect_params = item.rect_params
        x_start, y_start, x_end, y_end = cal_rect_params(rect_params)

        item_bbox = ((x_start, y_start), (x_end, y_end))

        left_area = overlapped(bag_left.bbox, item_bbox)
        right_area = overlapped(bag_right.bbox, item_bbox)

        bag_left_overlapped = left_area > BAG_MIN_OVERLAP_PERC
        bag_right_overlapped = right_area > BAG_MIN_OVERLAP_PERC

        if not bag_left_overlapped and not bag_right_overlapped:
            continue
        
        if left_area > BAG_MAX_OVERLAP_PERC or right_area > BAG_MAX_OVERLAP_PERC:
            continue

        elif bag_left_overlapped:
            inter_communi_pods(2, item_dict, item, left_action_set)
        
        elif bag_right_overlapped:
            inter_communi_pods(1, item_dict, item, right_action_set)

