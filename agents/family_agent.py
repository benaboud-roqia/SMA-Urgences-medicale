from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
import json
import random

# Contacts famille algeriens (noms + numeros algeriens reels)
ALGERIAN_NAMES = [
    ("Karim Benali", "0550-12-34-56"),
    ("Fatima Bouzid", "0661-98-76-54"),
    ("Mohamed Cherif", "0770-45-67-89"),
    ("Amina Hadj", "0555-32-10-98"),
    ("Youcef Meziane", "0699-11-22-33"),
    ("Nadia Khelifi", "0560-44-55-66"),
    ("Rachid Boukhalfa", "0771-77-88-99"),
    ("Samira Aouadi", "0550-66-77-88"),
    ("Djamel Ferhat", "0662-33-44-55"),
    ("Houria Mansouri", "0556-99-00-11"),
    ("Abdelkader Tlemcani", "0770-22-33-44"),
    ("Meriem Saidi", "0661-55-66-77"),
    ("Sofiane Belkacem", "0550-88-99-00"),
    ("Lynda Hamidi", "0699-44-55-66"),
    ("Omar Bensalem", "0771-11-22-33"),
]

class FamilyAgent(Agent):
    """Agent 10 - Notifie la famille du patient en temps reel."""

    class HandleFamilyNotifyBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                data = json.loads(msg.body)
                call_id = data["call_id"]
                summary = data["summary"]

                contact = random.choice(ALGERIAN_NAMES)
                nom, tel = contact

                print(f"\n[FamilyAgent] NOTIFICATION FAMILLE pour {call_id}")
                print(f"  Contact: {nom} | Tel: {tel}")
                print(f"  Message: {summary}")
                print(f"  [SMS envoye au {tel}]")

    async def setup(self):
        print("[FamilyAgent] Demarrage...")
        template = Template()
        template.set_metadata("type", "family_notify")
        self.add_behaviour(self.HandleFamilyNotifyBehaviour(), template)