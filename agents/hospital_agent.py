from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
import json
import random

# Hopitaux reels en Algerie avec leurs services
HOSPITALS_ALGERIA = [
    {
        "name": "CHU Mustapha Pacha",
        "ville": "Alger",
        "adresse": "Place du 1er Mai, Alger",
        "tel": "021-23-53-53",
        "urgences": "021-23-50-50",
        "specialites": ["Reanimation", "Chirurgie", "Cardiologie", "Neurologie"]
    },
    {
        "name": "CHU Beni Messous",
        "ville": "Alger",
        "adresse": "Route de Beni Messous, Alger",
        "tel": "021-93-15-00",
        "urgences": "021-93-15-00",
        "specialites": ["Reanimation", "Chirurgie", "Pediatrie", "Traumatologie"]
    },
    {
        "name": "CHU Nafissa Hamoud (ex Parnet)",
        "ville": "Alger",
        "adresse": "Hussein Dey, Alger",
        "tel": "021-49-11-18",
        "urgences": "021-49-11-18",
        "specialites": ["Maternite", "Gynecologie", "Neonatologie"]
    },
    {
        "name": "EHU 1er Novembre Oran",
        "ville": "Oran",
        "adresse": "BP 4166 Ibn Rochd, Oran",
        "tel": "041-41-27-27",
        "urgences": "041-41-27-27",
        "specialites": ["Reanimation", "Chirurgie", "Cardiologie", "Neurochirurgie"]
    },
    {
        "name": "CHU Ibn Badis Constantine",
        "ville": "Constantine",
        "adresse": "Rue Freres Bouadou, Constantine",
        "tel": "031-92-50-50",
        "urgences": "031-92-50-50",
        "specialites": ["Reanimation", "Chirurgie", "Traumatologie", "Cardiologie"]
    },
    {
        "name": "CHU Ibn Rochd Annaba",
        "ville": "Annaba",
        "adresse": "Cité Sakamody, Annaba",
        "tel": "038-86-60-60",
        "urgences": "038-86-60-60",
        "specialites": ["Reanimation", "Chirurgie", "Medecine interne"]
    },
    {
        "name": "CHU Saadna Abdenour Setif",
        "ville": "Setif",
        "adresse": "Route de Ain Arnat, Setif",
        "tel": "036-90-90-90",
        "urgences": "036-90-90-90",
        "specialites": ["Reanimation", "Chirurgie", "Cardiologie"]
    },
    {
        "name": "EPH Frantz Fanon Blida",
        "ville": "Blida",
        "adresse": "Route de Boufarik, Blida",
        "tel": "025-41-10-10",
        "urgences": "025-41-10-10",
        "specialites": ["Psychiatrie", "Neurologie", "Medecine generale"]
    },
    {
        "name": "CHU Tizi Ouzou",
        "ville": "Tizi Ouzou",
        "adresse": "Cite Oued Aissi, Tizi Ouzou",
        "tel": "026-21-85-85",
        "urgences": "026-21-85-85",
        "specialites": ["Reanimation", "Chirurgie", "Traumatologie"]
    },
    {
        "name": "CHU Abdelkader Hassaine Tlemcen",
        "ville": "Tlemcen",
        "adresse": "Rue Dr Tidjani Damerdji, Tlemcen",
        "tel": "043-27-42-42",
        "urgences": "043-27-42-42",
        "specialites": ["Reanimation", "Chirurgie", "Cardiologie"]
    },
]

UNITS = {
    "CRITICAL": "Reanimation",
    "HIGH": "Urgences chirurgicales",
    "MEDIUM": "Urgences medicales",
    "LOW": "Consultation rapide"
}

class HospitalAgent(Agent):
    """Agent 4 - Gere les lits et prepare l accueil dans les hopitaux algeriens."""

    available_beds = {"Reanimation": 3, "Urgences chirurgicales": 8, "Urgences medicales": 15, "Consultation rapide": 20}

    class HandlePrepareRequestBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                data = json.loads(msg.body)
                call_id = data["call_id"]
                severity = data["severity"]
                diagnosis = data.get("diagnosis", "N/A")

                unit = UNITS.get(severity, "Urgences medicales")
                beds = HospitalAgent.available_beds.get(unit, 0)

                # Choisir un hopital selon la severite
                if severity == "CRITICAL":
                    candidates = [h for h in HOSPITALS_ALGERIA if "Reanimation" in h["specialites"]]
                else:
                    candidates = HOSPITALS_ALGERIA
                hospital = random.choice(candidates)

                if beds > 0:
                    HospitalAgent.available_beds[unit] -= 1
                    status = "READY"
                    bed_number = f"LIT-{random.randint(100, 999)}"
                else:
                    status = "FULL"
                    bed_number = "N/A"
                    unit = "Urgences medicales"

                print(f"[HospitalAgent] {call_id} | Hopital: {hospital['name']} ({hospital['ville']})")
                print(f"  Unite: {unit} | Lit: {bed_number} | Tel urgences: {hospital['urgences']}")
                print(f"  Diagnostic recu: {diagnosis}")

                reply = Message(to="coordinator@localhost")
                reply.set_metadata("performative", "inform")
                reply.set_metadata("type", "hospital_ready")
                reply.body = json.dumps({
                    "call_id": call_id,
                    "status": status,
                    "unit": unit,
                    "bed": bed_number,
                    "hospital": hospital["name"],
                    "ville": hospital["ville"],
                    "tel": hospital["urgences"]
                })
                await self.send(reply)

    async def setup(self):
        print("[HospitalAgent] Demarrage...")
        template = Template()
        template.set_metadata("type", "prepare_request")
        self.add_behaviour(self.HandlePrepareRequestBehaviour(), template)