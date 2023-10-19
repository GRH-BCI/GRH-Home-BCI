import asyncio
from kasa import SmartPlug

''' 
    async function to handle turning the smart-plugs on/off. checks for the current state of the 
    device and IP length  
'''
async def handle_device(ip: str, duration: int):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    if len(ip) > 5:
        p = SmartPlug(ip)
        await p.update()  # Request the update
        print(p.is_on)
        if not p.is_on:
            await p.update()
            await p.turn_on()
            await asyncio.sleep(duration)
            await p.update()
            await p.turn_off()
        else:
            print("already on")
