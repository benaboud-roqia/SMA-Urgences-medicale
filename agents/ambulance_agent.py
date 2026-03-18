from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
import asyncio
import json
import random

class AmbulanceAgent(Agent):
    """Agent 3 - Dispatche une ambulance selon disponibilité."""

    class HandleDispatchBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                data = json.loads(msg.body)
                call_id = data["call_id"]
                severity = data["severity"]
                location = data["location"]

                # Simuler disponibilité et ETA
                available = random.choice([True, True, True, False])
                eta = random.randint(5, 20)
                status = "DISPATCHED" if available else "UNAVAILABLE"
                unit = f"AMB-{random.randint(1, 10):02d}"

                print(f"[AmbulanceAgent] 🚑 Dispatch {call_id} | Unité: {unit} | Statut: {status} | ETA: {eta} min")

                reply = Message(to="coordinator@localhost")
                reply.set_metadata("performative", "inform")
                reply.set_metadata("type", "ambulance_confirm")
                reply.body = json.dumps({
                    "call_id": call_id,
                    "status": status,
                    "unit": unit,
                    "eta": eta
                })
                await self.send(reply)

    async def setup(self):
        print("[AmbulanceAgent] 🟢 Démarrage...")
        template = Template()
        template.set_metadata("type", "dispatch_order")
        self.add_behaviour(self.HandleDispatchBehaviour(), template)
