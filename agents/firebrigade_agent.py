from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
import json
import asyncio
import random

class FireBrigadeAgent(Agent):
    """Agent 7 - Intervient si incendie ou désincarcération nécessaire."""

    class HandleSecureZoneBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                data = json.loads(msg.body)
                call_id = data["call_id"]
                location = data["location"]

                delay = random.uniform(1, 4)
                await asyncio.sleep(delay)

                action = random.choice(["Désincarcération", "Extinction incendie", "Sécurisation périmètre"])
                trucks = random.randint(1, 3)
                print(f"[FireBrigadeAgent] 🚒 {action} pour {call_id} à {location} | {trucks} camion(s)")

                reply = Message(to="coordinator@localhost")
                reply.set_metadata("performative", "inform")
                reply.set_metadata("type", "zone_secured")
                reply.body = json.dumps({
                    "call_id": call_id,
                    "status": "SECURED",
                    "agent": "firebrigade",
                    "action": action,
                    "trucks": trucks
                })
                await self.send(reply)

    async def setup(self):
        print("[FireBrigadeAgent] 🟢 Démarrage...")
        template = Template()
        template.set_metadata("type", "secure_zone")
        self.add_behaviour(self.HandleSecureZoneBehaviour(), template)
