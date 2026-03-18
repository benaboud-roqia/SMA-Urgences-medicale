import spade
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template
import asyncio
import random
import json

CALL_TYPES = ["accident", "cardiac_arrest", "fire", "trauma", "stroke", "intoxication", "fracture", "brulure"]
SEVERITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

# Lieux reels en Algerie
LOCATIONS = [
    "Alger - Bab El Oued",
    "Alger - Hussein Dey",
    "Alger - Kouba",
    "Alger - El Harrach",
    "Alger - Bir Mourad Rais",
    "Oran - Hai Es Salam",
    "Oran - Es Senia",
    "Oran - Bir El Djir",
    "Constantine - Ain Smara",
    "Constantine - El Khroub",
    "Annaba - El Bouni",
    "Setif - Ain Arnat",
    "Blida - Bougara",
    "Tizi Ouzou - Azazga",
    "Bejaia - Akbou",
    "Batna - Ain Touta",
    "Tlemcen - Mansourah",
    "Skikda - Azzaba",
    "Autoroute Est-Ouest - PK 142",
    "RN1 - Medea - Zone rurale",
]

# Numeros d urgence reels en Algerie
EMERGENCY_NUMBERS = {
    "SAMU": "115",
    "Police": "17",
    "Pompiers": "14",
    "Gendarmerie": "1055",
    "Protection Civile": "14",
    "SAMU Alger": "021-23-50-50",
    "SAMU Oran": "041-33-15-15",
    "SAMU Constantine": "031-92-50-50",
    "SAMU Annaba": "038-86-60-60",
    "Urgences CHU Mustapha": "021-23-53-53",
    "Urgences CHU Beni Messous": "021-93-15-00",
    "Urgences CHU Oran": "041-41-27-27",
}

class EmergencyAgent(Agent):
    """Agent 1 - Recoit les appels d urgence et evalue la situation."""

    call_counter = 0

    class GenerateEmergencyBehaviour(PeriodicBehaviour):
        async def run(self):
            EmergencyAgent.call_counter += 1
            call_id = f"CALL-{EmergencyAgent.call_counter:04d}"
            call_type = random.choice(CALL_TYPES)
            severity = random.choice(SEVERITIES)
            location = random.choice(LOCATIONS)

            # Choisir le bon numero selon la gravite
            if severity == "CRITICAL":
                numero = EMERGENCY_NUMBERS["SAMU"]
            elif call_type == "fire":
                numero = EMERGENCY_NUMBERS["Pompiers"]
            elif call_type == "accident":
                numero = EMERGENCY_NUMBERS["Gendarmerie"]
            else:
                numero = EMERGENCY_NUMBERS["SAMU"]

            print(f"\n[EmergencyAgent] Nouvel appel recu: {call_id}")
            print(f"  Type: {call_type} | Severite: {severity} | Lieu: {location}")
            print(f"  Numero appele: {numero}")

            msg = Message(to="coordinator@localhost")
            msg.set_metadata("performative", "inform")
            msg.set_metadata("type", "emergency_call")
            msg.body = json.dumps({
                "call_id": call_id,
                "type": call_type,
                "severity": severity,
                "location": location,
                "numero": numero
            })
            await self.send(msg)
            print(f"[EmergencyAgent] Appel {call_id} transmis au coordinateur.")

    class ReceiveResolutionBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            if msg:
                data = json.loads(msg.body)
                print(f"\n[EmergencyAgent] RESOLUTION RECUE pour {data.get('call_id')}")
                print(f"  Resume: {data.get('summary', 'N/A')}")

    async def setup(self):
        print("[EmergencyAgent] Demarrage...")
        gen = self.GenerateEmergencyBehaviour(period=20, start_at=None)
        self.add_behaviour(gen)
        template = Template()
        template.set_metadata("type", "resolution_status")
        recv = self.ReceiveResolutionBehaviour()
        self.add_behaviour(recv, template)