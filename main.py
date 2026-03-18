"""
Système Multi-Agents - Coordination des Urgences Médicales
==========================================================
SPADE 4.x avec serveur XMPP embarqué (pyjabber) — aucune config externe requise.
"""

import asyncio
import spade

from agents.emergency_agent import EmergencyAgent
from agents.coordinator_agent import CoordinatorAgent
from agents.ambulance_agent import AmbulanceAgent
from agents.hospital_agent import HospitalAgent
from agents.doctor_agent import DoctorAgent
from agents.police_agent import PoliceAgent
from agents.firebrigade_agent import FireBrigadeAgent
from agents.helicopter_agent import HelicopterAgent
from agents.bloodbank_agent import BloodBankAgent
from agents.family_agent import FamilyAgent

PASSWORD = "password123"

AGENTS_CONFIG = [
    ("emergency@localhost",    PASSWORD, EmergencyAgent),
    ("coordinator@localhost",  PASSWORD, CoordinatorAgent),
    ("ambulance@localhost",    PASSWORD, AmbulanceAgent),
    ("hospital@localhost",     PASSWORD, HospitalAgent),
    ("doctor@localhost",       PASSWORD, DoctorAgent),
    ("police@localhost",       PASSWORD, PoliceAgent),
    ("firebrigade@localhost",  PASSWORD, FireBrigadeAgent),
    ("helicopter@localhost",   PASSWORD, HelicopterAgent),
    ("bloodbank@localhost",    PASSWORD, BloodBankAgent),
    ("family@localhost",       PASSWORD, FamilyAgent),
]


async def main():
    print("=" * 60)
    print("  🚨 Système de Coordination des Urgences Médicales 🚨")
    print("=" * 60)

    agents = []

    for jid, pwd, AgentClass in AGENTS_CONFIG:
        agent = AgentClass(jid, pwd)
        await agent.start(auto_register=True)
        agents.append(agent)
        print(f"  ✅ {jid} démarré")

    print("\n[Main] Tous les agents sont actifs. Simulation en cours...")
    print("[Main] Appuyez sur Ctrl+C pour arrêter.\n")

    try:
        while True:
            await asyncio.sleep(1)
            if all(not agent.is_alive() for agent in agents):
                print("[Main] Tous les agents se sont arrêtés.")
                break
    except KeyboardInterrupt:
        print("\n[Main] Arrêt demandé...")
    finally:
        for agent in agents:
            if agent.is_alive():
                await agent.stop()
        print("[Main] Simulation terminée.")


if __name__ == "__main__":
    spade.run(main(), embedded_xmpp_server=True)
