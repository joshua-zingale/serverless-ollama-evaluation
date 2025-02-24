import threading
import time
from helpers import *

async def answer(question):
    async for resp in request(question, stream = True):
        
print(counts)