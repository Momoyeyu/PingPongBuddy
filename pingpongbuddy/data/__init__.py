import json
import os

def load_places():
    """
    加载场地数据
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    places_file = os.path.join(current_dir, 'places.json')
    
    with open(places_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data['places'] 