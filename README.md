# HELIOS

## Project Overview

Modern applications and computer systems generate large amounts of operational data such as CPU usage, memory consumption, disk activity, and network traffic.

HELIOS collects this telemetry from a monitored computer and sends it to a central Flask backend, where the data can be analysed for abnormal behaviour and potential system issues.

The project aims to move beyond simple monitoring by combining:

* Real-time system monitoring
* Historical telemetry storage
* Rule-based diagnostics
* Statistical anomaly detection
* Machine-learning-based anomaly detection
* Process-level monitoring
* AI-assisted system analysis
* Web-based visualisation

---

##  Features

*  Real-time CPU, RAM, disk and network monitoring
*  Anomaly detection
*  Isolation Forest machine learning
*  Historical telemetry analysis
*  Process monitoring
*  AI-assisted system analysis
*  Web-based dashboard
*  SQLite telemetry storage
*  Standalone HELIOS Agent

---

##  Architecture

```text
Computer
   │
   ▼
HELIOS Agent
   │
   │ Telemetry
   ▼
Flask Backend
   │
   ├── Anomaly Detection
   ├── Process Analysis
   ├── AI Analysis
   └── SQLite
        │
        ▼
   HELIOS Dashboard
```

---

##  Technology Stack

**Backend**

* Python
* Flask
* SQLite
* Pandas
* NumPy
* Scikit-learn
* psutil

**Frontend**

* HTML
* CSS
* JavaScript
* Chart.js

**AI**

* Google Gemini

**Tools**

* Git
* GitHub
* VS Code
* PyInstaller

---

## Project Structure

```text
System_Analysis_Project/
│
├── requirements.txt
├── .gitignore
│
└── src/
    ├── agent/
    ├── ai/
    ├── api/
    ├── core/
    ├── database/
    ├── logs/
    ├── web/
    └── app.py
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/SarahPaul926/system-observability-platform.git
```

Enter the project:

```bash
cd system-observability-platform
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running HELIOS

From the `src` directory:

```powershell
cd src
python app.py
```

The HELIOS dashboard will then be available through the Flask server.

---

## HELIOS Agent

The HELIOS Agent collects telemetry from the monitored computer and sends it to the HELIOS backend.
HELIOS-Agent.exe is present in the src/dist
The repository will provide a pre-built:

```text
HELIOS-Agent.exe
```

Run the Agent on the computer you want to monitor, then open the HELIOS dashboard.

---

## Testing

Database tests:

```powershell
python -m database.test_db
```

Database stress test:

```powershell
python -m database.stress_test
```

Analytics:

```powershell
python -m database.analytics
```

---

## Deployment

The HELIOS backend is deployed using **Flask + Gunicorn**.

Live dashboard:

**https://helios-observability.onrender.com/**

---

## Future Development

* Independent Agent-to-computer association
* Improved root-cause analysis
* Better AI recommendations
* Persistent production database
* Authentication
* Alert notifications
* Improved production architecture

---

## Author

**Sarah Paul**
BSc Software Engineering
University of Stirling
