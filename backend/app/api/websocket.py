"""
WebSocket endpoint for the live simulation.

Design choice: each browser tab that connects gets its OWN SimulationEngine
instance - not a shared colony across multiple viewers. That matches what
Phase 2 already did (simulation ran per-browser-tab), just moved server-side
now. A shared multi-viewer colony is a reasonable future extension, but
adding that concurrency complexity now would make it harder to verify the
port from Phase 1/2 is correct - one thing changing at a time.

Protocol (JSON messages the frontend sends over the socket):
  {"action": "start"}
  {"action": "pause"}
  {"action": "reset", "numAnts": 30}
  {"action": "setSpeed", "ticksPerSecond": 20}

Protocol (JSON the backend sends back, every tick while running):
  see SimulationEngine.get_state()
"""

import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.simulation.engine import SimulationEngine

router = APIRouter()


@router.websocket("/ws/simulation")
async def simulation_socket(websocket: WebSocket):
    await websocket.accept()

    engine = SimulationEngine()
    running = False
    ticks_per_second = 10  # how many simulation ticks to send per real second

    try:
        while True:
            # Check for an incoming control message without blocking the
            # simulation loop for long - short timeout, then proceed.
            try:
                raw = await asyncio.wait_for(websocket.receive_text(), timeout=0.01)
                message = json.loads(raw)
                action = message.get("action")

                if action == "start":
                    running = True
                elif action == "pause":
                    running = False
                elif action == "reset":
                    num_ants = message.get("numAnts", engine.num_ants)
                    engine.reset(num_ants=num_ants)
                    running = False
                    await websocket.send_json(engine.get_state())
                elif action == "setSpeed":
                    ticks_per_second = max(1, min(60, message.get("ticksPerSecond", 10)))

            except asyncio.TimeoutError:
                pass  # no message waiting - fine, keep simulating

            if running:
                engine.tick()
                await websocket.send_json(engine.get_state())
                await asyncio.sleep(1.0 / ticks_per_second)
            else:
                await asyncio.sleep(0.05)  # idle, avoid busy-looping while paused

    except WebSocketDisconnect:
        pass
