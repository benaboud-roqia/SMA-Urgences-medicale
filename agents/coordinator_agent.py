import spade
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State, CyclicBehaviour
from spade.message import Message
from spade.template import Template
import asyncio
import json

# États FSM
STATE_IDLE = "IDLE"
STATE_DISPATCHING = "DISPATCHING"
STATE_MEDICAL_RESPONSE = "MEDICAL_RESPONSE"
STATE_SECURING = "SECURING"
STATE_PREPARING = "PREPARING"
STATE_RESOLVING = "RESOLVING"


class CoordinatorAgent(Agent):
    """Agent 2 - Orchestre toute la chaîne de réponse via FSMBehaviour."""

    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.current_call = None
        self.diagnosis = None
        self.dispatch_confirmed = False
        self.blood_confirmed = False
        self.zone_secured = False
        self.hospital_ready = False

    class IdleState(State):
        async def run(self):
            print(f"\n[Coordinator] 🔵 État: IDLE — En attente d'un appel...")
            msg = await self.receive(timeout=30)
            if msg and msg.metadata.get("type") == "emergency_call":
                data = json.loads(msg.body)
                self.agent.current_call = data
                self.agent.dispatch_confirmed = False
                self.agent.blood_confirmed = False
                self.agent.zone_secured = False
                self.agent.hospital_ready = False
                self.agent.diagnosis = None
                print(f"[Coordinator] 📥 Appel reçu: {data['call_id']} | {data['severity']}")
                self.set_next_state(STATE_DISPATCHING)
            else:
                self.set_next_state(STATE_IDLE)

    class DispatchingState(State):
        async def run(self):
            call = self.agent.current_call
            print(f"\n[Coordinator] 🚑 État: DISPATCHING — {call['call_id']}")

            if call["severity"] == "CRITICAL" and "rural" in call["location"].lower():
                # Envoyer hélicoptère
                msg = Message(to="helicopter@localhost")
                msg.set_metadata("performative", "request")
                msg.set_metadata("type", "helicopter_order")
                msg.body = json.dumps({"call_id": call["call_id"], "severity": call["severity"], "location": call["location"]})
                await self.send(msg)
                print(f"[Coordinator] 🚁 Ordre hélicoptère envoyé.")
                # Attendre confirmation hélicoptère
                confirm = await self.receive(timeout=10)
                if confirm and confirm.metadata.get("type") in ("helicopter_confirm", "ambulance_confirm"):
                    print(f"[Coordinator] ✅ Dispatch confirmé: {json.loads(confirm.body)}")
            else:
                # Envoyer ambulance
                msg = Message(to="ambulance@localhost")
                msg.set_metadata("performative", "request")
                msg.set_metadata("type", "dispatch_order")
                msg.body = json.dumps({"call_id": call["call_id"], "severity": call["severity"], "location": call["location"]})
                await self.send(msg)
                print(f"[Coordinator] 🚑 Ordre ambulance envoyé.")
                confirm = await self.receive(timeout=10)
                if confirm and confirm.metadata.get("type") in ("ambulance_confirm", "helicopter_confirm"):
                    print(f"[Coordinator] ✅ Dispatch confirmé: {json.loads(confirm.body)}")

            self.set_next_state(STATE_MEDICAL_RESPONSE)

    class MedicalResponseState(State):
        async def run(self):
            call = self.agent.current_call
            print(f"\n[Coordinator] 🩺 État: MEDICAL_RESPONSE — {call['call_id']}")

            # Demande diagnostic au médecin
            msg = Message(to="doctor@localhost")
            msg.set_metadata("performative", "request")
            msg.set_metadata("type", "medical_request")
            msg.body = json.dumps({"call_id": call["call_id"], "type": call["type"], "severity": call["severity"]})
            await self.send(msg)

            # Demande banque de sang
            blood_types = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
            import random
            msg2 = Message(to="bloodbank@localhost")
            msg2.set_metadata("performative", "request")
            msg2.set_metadata("type", "blood_request")
            msg2.body = json.dumps({"call_id": call["call_id"], "blood_type": random.choice(blood_types)})
            await self.send(msg2)

            # Attendre diagnostic + confirmation sang
            for _ in range(2):
                resp = await self.receive(timeout=10)
                if resp:
                    rtype = resp.metadata.get("type")
                    if rtype == "diagnosis":
                        self.agent.diagnosis = json.loads(resp.body)
                        print(f"[Coordinator] 🩺 Diagnostic reçu: {self.agent.diagnosis}")
                    elif rtype == "blood_confirm":
                        print(f"[Coordinator] 🩸 Sang confirmé: {json.loads(resp.body)}")

            self.set_next_state(STATE_SECURING)

    class SecuringState(State):
        async def run(self):
            call = self.agent.current_call
            print(f"\n[Coordinator] 🔒 État: SECURING — {call['call_id']}")

            payload = json.dumps({"call_id": call["call_id"], "location": call["location"]})

            msg_police = Message(to="police@localhost")
            msg_police.set_metadata("performative", "request")
            msg_police.set_metadata("type", "secure_zone")
            msg_police.body = payload
            await self.send(msg_police)

            msg_fire = Message(to="firebrigade@localhost")
            msg_fire.set_metadata("performative", "request")
            msg_fire.set_metadata("type", "secure_zone")
            msg_fire.body = payload
            await self.send(msg_fire)

            # Attendre 2 confirmations
            for _ in range(2):
                resp = await self.receive(timeout=10)
                if resp and resp.metadata.get("type") == "zone_secured":
                    print(f"[Coordinator] ✅ Zone sécurisée par: {resp.sender}")

            self.set_next_state(STATE_PREPARING)

    class PreparingState(State):
        async def run(self):
            call = self.agent.current_call
            diag = self.agent.diagnosis or {}
            print(f"\n[Coordinator] 🏥 État: PREPARING — {call['call_id']}")

            msg = Message(to="hospital@localhost")
            msg.set_metadata("performative", "request")
            msg.set_metadata("type", "prepare_request")
            msg.body = json.dumps({
                "call_id": call["call_id"],
                "severity": call["severity"],
                "diagnosis": diag.get("instructions", "N/A")
            })
            await self.send(msg)

            resp = await self.receive(timeout=10)
            if resp and resp.metadata.get("type") == "hospital_ready":
                print(f"[Coordinator] 🏥 Hôpital prêt: {json.loads(resp.body)}")

            self.set_next_state(STATE_RESOLVING)

    class ResolvingState(State):
        async def run(self):
            call = self.agent.current_call
            diag = self.agent.diagnosis or {}
            print(f"\n[Coordinator] 🏁 État: RESOLVING — {call['call_id']}")

            summary = (
                f"Appel {call['call_id']} résolu. "
                f"Type: {call['type']}, Sévérité: {call['severity']}, "
                f"Lieu: {call['location']}. "
                f"Instructions: {diag.get('instructions', 'N/A')}."
            )

            # Notifier la famille
            msg_fam = Message(to="family@localhost")
            msg_fam.set_metadata("performative", "inform")
            msg_fam.set_metadata("type", "family_notify")
            msg_fam.body = json.dumps({"call_id": call["call_id"], "summary": summary})
            await self.send(msg_fam)

            # Notifier l'agent d'urgence
            msg_em = Message(to="emergency@localhost")
            msg_em.set_metadata("performative", "inform")
            msg_em.set_metadata("type", "resolution_status")
            msg_em.body = json.dumps({"call_id": call["call_id"], "summary": summary})
            await self.send(msg_em)

            print(f"[Coordinator] ✅ Résolution complète: {summary}")
            self.set_next_state(STATE_IDLE)

    async def setup(self):
        print("[CoordinatorAgent] 🟢 Démarrage FSM...")

        fsm = FSMBehaviour()
        fsm.add_state(name=STATE_IDLE, state=self.IdleState(), initial=True)
        fsm.add_state(name=STATE_DISPATCHING, state=self.DispatchingState())
        fsm.add_state(name=STATE_MEDICAL_RESPONSE, state=self.MedicalResponseState())
        fsm.add_state(name=STATE_SECURING, state=self.SecuringState())
        fsm.add_state(name=STATE_PREPARING, state=self.PreparingState())
        fsm.add_state(name=STATE_RESOLVING, state=self.ResolvingState())

        fsm.add_transition(source=STATE_IDLE, dest=STATE_IDLE)
        fsm.add_transition(source=STATE_IDLE, dest=STATE_DISPATCHING)
        fsm.add_transition(source=STATE_DISPATCHING, dest=STATE_MEDICAL_RESPONSE)
        fsm.add_transition(source=STATE_MEDICAL_RESPONSE, dest=STATE_SECURING)
        fsm.add_transition(source=STATE_SECURING, dest=STATE_PREPARING)
        fsm.add_transition(source=STATE_PREPARING, dest=STATE_RESOLVING)
        fsm.add_transition(source=STATE_RESOLVING, dest=STATE_IDLE)

        self.add_behaviour(fsm)
