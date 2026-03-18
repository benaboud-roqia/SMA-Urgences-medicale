from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
import json
import random

DIAGNOSES = {
    "accident": ("Traumatisme multiple", "Immobilisation, perfusion IV, antidouleurs"),
    "cardiac_arrest": ("Arrêt cardiaque", "RCP, défibrillation, adrénaline IV"),
    "fire": ("Brûlures et inhalation de fumée", "Oxygène, pansements stériles, morphine"),
    "trauma": ("Traumatisme crânien", "Scanner urgent, surveillance neurologique"),
    "stroke": ("AVC ischémique", "Thrombolyse si < 4h30, scanner cérébral"),
}

MEDICATIONS = ["Morphine 10mg", "Adrénaline 1mg", "Aspirine 300mg", "Héparine 5000UI", "Paracétamol 1g"]

class DoctorAgent(Agent):
    """Agent 5 - Donne un pré-diagnostic et les instructions médicales."""

    class HandleMedicalRequestBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                data = json.loads(msg.body)
                call_id = data["call_id"]
                call_type = data["type"]
                severity = data["severity"]

                diag_label, instructions = DIAGNOSES.get(call_type, ("Inconnu", "Surveillance générale"))
                medication = random.choice(MEDICATIONS)

                print(f"[DoctorAgent] 🩺 Diagnostic pour {call_id}: {diag_label}")
                print(f"  Instructions: {instructions} | Médicament: {medication}")

                reply = Message(to="coordinator@localhost")
                reply.set_metadata("performative", "inform")
                reply.set_metadata("type", "diagnosis")
                reply.body = json.dumps({
                    "call_id": call_id,
                    "diagnosis": diag_label,
                    "instructions": instructions,
                    "medication": medication
                })
                await self.send(reply)

    async def setup(self):
        print("[DoctorAgent] 🟢 Démarrage...")
        template = Template()
        template.set_metadata("type", "medical_request")
        self.add_behaviour(self.HandleMedicalRequestBehaviour(), template)
