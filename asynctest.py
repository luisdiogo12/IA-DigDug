import asyncio
import getpass
import json
import os
import websockets

async def test_a():
    t = 0;
    while t <1000000000:
        t += 1
        if t % 100000000 == 0:
        	print(t)
        #await asyncio.sleep(100) 
def test_b():
    t = 0;
    while t <1000000000:
        t += 1
        if t % 100000000 == 0:
        	print(t)
async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
        key = ""
        while True:
            try:
                state = json.loads(													#?: receive game update, this must be called timely 
                    await websocket.recv()											#?:or your game will get out of sync with the server
                )  
                
                test_b()
                #await test_a()
                
                
                if key == None:
                    print("ERRO: key == None")
                    key = ""
                await websocket.send(												#?: send key command to server - you must implement
                    json.dumps({"cmd": "key", "key": key})							#?:this send in the AI agent
                )             
            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return
# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))