# Encrypted Notes App

A secure, locally-hosted notes application with end-to-end encryption and digital signatures.

Features
-  Client-side encryption using Fernet
-  Ed25519 digital signatures for tamper detection
-  Encrypted keyword search
-  Modern React UI with responsive design
-  Local SQLite storage

How to Run:

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload


cd frontend
npm install
npm run dev

- All notes encrypted before storage
- Digital signatures verify data integrity
- Persistent key management
- Search through encrypted keywords
