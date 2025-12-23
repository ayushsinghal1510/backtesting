import asyncio
import time
import inspect
import functools
from functools import partial

from ._services import (
    _parse_bool , 
    _parse_list ,
)

from logging import Logger

def method_log_timer(func) : 
    '''
    Decorator to log the execution time of a method.
    
    Args : 
        - func (callable): The method to be decorated.
        
    Returns : 
        - callable: The wrapped method with logging functionality.
    '''

    @functools.wraps(func)
    async def async_wrapper(self, *args , **kwargs) : 
        '''
        Asynchronous wrapper for the method to log execution time.
        
        Args : 
            - self: The instance of the class.
            - *args: Positional arguments for the method.
            - **kwargs: Keyword arguments for the method.
            
        Returns : 
            - result: The result of the method execution.
        '''

        logger : Logger | None = getattr(self , 'logger' , None)
        
        start_time = time.perf_counter()
        result = await func(self , *args , **kwargs)
        duration = time.perf_counter() - start_time
        
        if logger : logger.info(f'⏱️ Execution time for "{func.__name__}": "{duration:.4f}" seconds , response : "{result}"')
        else : print(f'Self.logger not found')

        return result

    @functools.wraps(func)
    def sync_wrapper(self, *args, **kwargs) : 
        '''
        Synchronous wrapper for the method to log execution time.
        
        Args :
            - self: The instance of the class.
            - *args: Positional arguments for the method.
            - **kwargs: Keyword arguments for the method.
            
        Returns : 
            - result: The result of the method execution.
        '''

        logger : Logger | None = getattr(self , 'logger' , None)

        start_time = time.perf_counter()
        result = func(self , *args , **kwargs)
        duration = time.perf_counter() - start_time

        if logger : logger.info(f'⏱️ Execution time for "{func.__name__}" : {duration:.4f} seconds , response : "{result}"')
        else : print(f'Self.logger not found')

        return result

    if inspect.iscoroutinefunction(func) : return async_wrapper
    else : return sync_wrapper

async def run_in_thread(
    func , 
    *args , 
    **kwargs
) : 

    loop = asyncio.get_running_loop() 
    
    func_part = partial(func , *args , **kwargs)

    return await loop.run_in_executor(None , func_part)

async def parse_list_async(value : str) -> list : return await run_in_thread(_parse_list , value)
async def parse_bool_async(value : str) -> bool : return await run_in_thread(_parse_bool , value)

def parse_list(value : str) -> list : return _parse_list(value)
def parse_bool(value : str) -> bool : return _parse_bool(value)

def env_str_to_list(
    value : str ,  
    default : str = '*'
) -> list : 

    if not value : value = default
    return _parse_list(value)

def env_str_to_bool(
    value : str , 
    default : str = 'True'
) -> bool : 

    if not value : value = default
    return _parse_bool(value)