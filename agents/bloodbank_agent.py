from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
import json
import random

class BloodBankAgent(Agent):
    """Agent 9 - Vérifie et réserve le groupe sanguin nécessaire."""

    # Stock simulé
    STOCK = {
        "A+": 15, "A-": 8, "B+": 12, "B-": 5,
        "O+": 20, "O-": 10, "AB+": 6, "AB-": 3
    }

    class HandleBloodRequestBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                data = json.loads(msg.body)
                call_id = data["call_id"]
                blood_type = data["blood_type"]

                stock = BloodBankAgent.STOCK.get(blood_type, 0)
                units_needed = random.randint(2, 4)
                available = stock >= units_needed

                if available:
                    BloodBankAgent.STOCK[blood_type] = stock - units_needed
                    status = "RESERVED"
                else:
                    status = "INSUFFICIENT"
                    units_needed = stock

                print(f"[BloodBankAgent] 🩸 {call_id} | Groupe: {blood_type} | Statut: {status} | Unités: {units_needed}")

                reply = Message(to="coordinator@localhost")
                reply.set_metadata("performative", "inform")
                reply.set_metadata("type", "blood_confirm")
                reply.body = json.dumps({
                    "call_id": call_id,
                    "blood_type": blood_type,
                    "status": status,
                    "units": units_needed
                })
                await self.send(reply)

    async def setup(self):
        print("[BloodBankAgent] 🟢 Démarrage...")
        template = Template()
        template.set_metadata("type", "blood_request")
        self.add_behaviour(self.HandleBloodRequestBehaviour(), template)
