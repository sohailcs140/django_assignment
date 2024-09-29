from django.core.cache import cache
import json
from django.conf import settings


def store_in_cache(key:str, value:object, version:int=1, timeout:int=settings.DEFAULT_TIME_OUT):        
        
        cache.set(key=key, value=json.dumps(value), version=version, timeout=timeout)
        


def get_from_cache(key:str, version:int=1):
    
    cache_data = cache.get(key=key, version=version)
    
    if cache_data:
        return json.loads(cache_data)
    
    return None


def delete_from_cache(key:str, version:int=1):
    
    cache.delete(key=key, version=version)