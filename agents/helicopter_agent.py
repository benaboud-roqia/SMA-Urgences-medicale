from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
import json
import random

class HelicopterAgent(Agent):
    """Agent 8 - SMUR héliporté pour les cas CRITICAL en zones éloignées."""

    class HandleHelicopterOrderBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                data = json.loads(msg.body)
                call_id = data["call_id"]
                severity = data["severity"]
                location = data["location"]

                eta = random.randint(10, 30)
                status = "AIRBORNE"
                unit = f"HELI-{random.randint(1, 3):02d}"

                print(f"[HelicopterAgent] 🚁 Décollage pour {call_id} | Unité: {unit} | ETA: {eta} min | Lieu: {location}")

                reply = Message(to="coordinator@localhost")
                reply.set_metadata("performative", "inform")
                reply.set_metadata("type", "helicopter_confirm")
                reply.body = json.dumps({
                    "call_id": call_id,
                    "status": status,
                    "unit": unit,
                    "eta": eta
                })
                await self.send(reply)

    async def setup(self):
        print("[HelicopterAgent] 🟢 Démarrage...")
        template = Template()
        template.set_metadata("type", "helicopter_order")
        self.add_behaviour(self.HandleHelicopterOrderBehaviour(), template)
