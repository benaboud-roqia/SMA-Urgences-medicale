from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
import json
import asyncio
import random

class PoliceAgent(Agent):
    """Agent 6 - Sécurise la zone et gère la circulation."""

    class HandleSecureZoneBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                data = json.loads(msg.body)
                call_id = data["call_id"]
                location = data["location"]

                delay = random.uniform(1, 3)
                await asyncio.sleep(delay)

                units = random.randint(2, 5)
                print(f"[PoliceAgent] 🚔 Zone sécurisée pour {call_id} à {location} | {units} unités déployées")

                reply = Message(to="coordinator@localhost")
                reply.set_metadata("performative", "inform")
                reply.set_metadata("type", "zone_secured")
                reply.body = json.dumps({
                    "call_id": call_id,
                    "status": "SECURED",
                    "agent": "police",
                    "units": units
                })
                await self.send(reply)

    async def setup(self):
        print("[PoliceAgent] 🟢 Démarrage...")
        template = Template()
        template.set_metadata("type", "secure_zone")
        self.add_behaviour(self.HandleSecureZoneBehaviour(), template)
