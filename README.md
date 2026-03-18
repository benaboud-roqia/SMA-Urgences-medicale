# SMA Urgences Medicales - Algerie

Systeme Multi-Agents de coordination des urgences medicales, developpe avec **SPADE 4** (Python 3.12).

## Equipe

| Nom | Role |
|-----|------|
| BENABOUD ROQIA | AI&SD |
| GAGAA IMANE | AI&SD |
| GASMI CHAIMA |AI&SD |
| ROUABEH NIAMAT-ALLAH |AI&SD|

## Description

Simulation d un systeme de coordination d urgences medicales en Algerie impliquant **10 agents autonomes** qui communiquent via XMPP. Le systeme couvre le cycle complet : appel d urgence -> dispatch -> reponse medicale -> securisation -> hospitalisation -> notification famille.
<img width="3455" height="1787" alt="image" src="https://github.com/user-attachments/assets/0151b98d-6dd9-4364-912d-44de407e5394" />

## Les 10 Agents

| # | Agent | JID | Role |
|---|-------|-----|------|
| 1 | EmergencyAgent | emergency@localhost | Genere les appels d urgence (lieux reels algeriens) |
| 2 | CoordinatorAgent | coordinator@localhost | Orchestre via FSMBehaviour (5 etats) |
| 3 | AmbulanceAgent | ambulance@localhost | Dispatch ambulance |
| 4 | HospitalAgent | hospital@localhost | Gere les lits (hopitaux reels algeriens) |
| 5 | DoctorAgent | doctor@localhost | Pre-diagnostic medical |
| 6 | PoliceAgent | police@localhost | Securisation de zone |
| 7 | FireBrigadeAgent | firebrigade@localhost | Intervention incendie/desincarceration |
| 8 | HelicopterAgent | helicopter@localhost | SMUR heliporte (cas CRITICAL) |
| 9 | BloodBankAgent | bloodbank@localhost | Reserve le groupe sanguin |
| 10 | FamilyAgent | family@localhost | Notifie la famille (contacts algeriens) |

## Flux FSM (CoordinatorAgent)

```
IDLE -> DISPATCHING -> MEDICAL_RESPONSE -> SECURING -> PREPARING -> RESOLVING -> IDLE
```

## Numeros d urgence integres (Algerie)

- SAMU National : **115**
- Police : **17**
- Pompiers / Protection Civile : **14**
- Gendarmerie : **1055**
- SAMU Alger : 021-23-50-50
- SAMU Oran : 041-33-15-15
- SAMU Constantine : 031-92-50-50

## Hopitaux reels integres

- CHU Mustapha Pacha - Alger
- CHU Beni Messous - Alger
- EHU 1er Novembre - Oran
- CHU Ibn Badis - Constantine
- CHU Ibn Rochd - Annaba
- CHU Saadna Abdenour - Setif
- CHU Tizi Ouzou
- CHU Abdelkader Hassaine - Tlemcen

## Installation

```bash
# Python 3.12 requis
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Lancement

**Simulation console uniquement :**
```bash
python main.py
```

**Dashboard web (http://localhost:5000) :**
```bash
python server.py
```
Puis ouvrir http://localhost:5000 et cliquer sur "Demarrer".

## Structure

```
emergency_mas/
├── main.py                  # Point d entree
├── server.py                # Serveur Flask + SSE
├── requirements.txt
├── agents/
│   ├── emergency_agent.py
│   ├── coordinator_agent.py  # FSM principal
│   ├── ambulance_agent.py
│   ├── hospital_agent.py     # Hopitaux algeriens
│   ├── doctor_agent.py
│   ├── police_agent.py
│   ├── firebrigade_agent.py
│   ├── helicopter_agent.py
│   ├── bloodbank_agent.py
│   └── family_agent.py
└── static/
    └── index.html            # Dashboard cyber theme
```

## Technologies

- Python 3.12
- SPADE 4.1.2 (Multi-Agent Systems)
- pyjabber (serveur XMPP embarque)
- Flask (dashboard web)
- Server-Sent Events (temps reel)
- HTML/CSS/JS (theme cyber)
