# Production Deploy Trigger - Mar 31 2026
import os
import json
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Tria de Mòduls API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase — supports env var (production) or local file (development)
if not firebase_admin._apps:
    cred_json = os.environ.get("FIREBASE_CREDENTIALS_JSON")
    cred_path = "serviceAccountKey.json"
    if cred_json:
        cred = credentials.Certificate(json.loads(cred_json))
        firebase_admin.initialize_app(cred)
        print("Firebase initialized from environment variable")
    elif os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print("Firebase initialized from local file")
    else:
        print("Warning: No Firebase credentials found")

db = firestore.client() if firebase_admin._apps else None


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()

@app.websocket("/tria/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# -- Autenticació --

class LoginRequest(BaseModel):
    username: str
    password: str

class UserCreateUpdate(BaseModel):
    password: str
    rol: str
    especialitats: List[str]

@app.post("/tria/login")
def login(creds: LoginRequest):
    try:
        if not db:
            raise HTTPException(status_code=500, detail="Database disabled")
        
        doc = db.collection("usuaris").document(creds.username).get()
        if not doc.exists:
            if creds.username == "admin" and creds.password == "123":
                db.collection("usuaris").document("admin").set({"password": "123", "rol": "ADMIN", "especialitats": []})
                return {"token": "fake-jwt-admin", "rol": "ADMIN", "especialitat": None, "username": "admin"}
            raise HTTPException(status_code=401, detail="Usuari no trobat")
            
        user_data = doc.to_dict()
        if creds.password != user_data.get("password"):
            raise HTTPException(status_code=401, detail="Contrasenya incorrecta")
            
        # Per compatibilitat de frontend, enviem sempre la primera especialitat com a singular
        esp_list = user_data.get("especialitats", [])
        primary_espc = esp_list[0] if esp_list else None
        
        return {
            "token": "fake-jwt-" + creds.username,
            "rol": user_data.get("rol"),
            "especialitat": primary_espc,
            "especialitats": esp_list, # Return full list
            "username": creds.username
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/usuaris/")
def get_usuaris():
    try:
        if not db: return []
        docs = db.collection("usuaris").stream()
        return [{"username": d.id, "rol": d.to_dict().get("rol"), "especialitats": d.to_dict().get("especialitats", [])} for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/usuaris/{username}")
def save_usuari(username: str, payload: UserCreateUpdate):
    try:
        if not db: return {"status": "success"}
        db.collection("usuaris").document(username).set({
            "password": payload.password,
            "rol": payload.rol,
            "especialitats": payload.especialitats
        })
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/usuaris/{username}")
def delete_usuari(username: str):
    try:
        if not db: return {"status": "success"}
        if username == "admin": raise HTTPException(status_code=400, detail="No pots eliminar l'administrador principal")
        db.collection("usuaris").document(username).delete()
        return {"status": "success"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class RenameUserPayload(BaseModel):
    new_username: str

@app.patch("/usuaris/rename/{old_username}")
def rename_usuari(old_username: str, payload: RenameUserPayload):
    try:
        if not db: return {"status": "success"}
        new_username = payload.new_username.strip()
        if not new_username:
            raise HTTPException(status_code=400, detail="El nou nom d'usuari no pot estar buit")
        
        old_ref = db.collection("usuaris").document(old_username)
        old_doc = old_ref.get()
        if not old_doc.exists:
            raise HTTPException(status_code=404, detail="Usuari no trobat")
        
        # Check if new username already exists
        if db.collection("usuaris").document(new_username).get().exists:
            raise HTTPException(status_code=400, detail="El nou nom d'usuari ja existeix")

        data = old_doc.to_dict()
        db.collection("usuaris").document(new_username).set(data)
        old_ref.delete()
        
        return {"status": "success"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/grups/")
def get_grups():
    try:
        if not db: return []
        docs = db.collection("grups").stream()
        return [{"name": d.id, "especialitats": d.to_dict().get("especialitats", [])} for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class GrupPayload(BaseModel):
    especialitats: List[str]

@app.post("/grups/{name}")
def create_grup(name: str, payload: GrupPayload):
    try:
        if not db: return {"status": "success"}
        db.collection("grups").document(name).set({
            "especialitats": payload.especialitats
        })
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/grups/{name}")
def delete_grup(name: str):
    try:
        if not db: return {"status": "success"}
        db.collection("grups").document(name).delete()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -- Estat Compartit per Especialitat --

@app.get("/tria/state/{especialitat}")
def get_tria_state(especialitat: str):
    try:
        if not db: return {"torn_actual": None, "fase": "PREPARACIO", "ordre": []}
        doc = db.collection("tria").document(especialitat).get()
        if doc.exists:
            return doc.to_dict()
        return {"torn_actual": None, "fase": "PREPARACIO", "ordre": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tria/state")
def get_all_states():
    try:
        if not db: return {}
        docs = db.collection("tria").stream()
        return {d.id: d.to_dict() for d in docs if d.id != "state"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SlotSelection(BaseModel):
    docent_id: str
    modul_id: str
    grup_id: str
    
@app.post("/tria/take")
async def take_modul(payload: SlotSelection):
    try:
        if not db: return {"status": "success", "slots_updated": 0}
        horaris_ref = db.collection("horaris")
        query = horaris_ref.where("modul_id", "==", payload.modul_id).where("grup_id", "==", payload.grup_id).stream()
        
        batch = db.batch()
        updated_slots = []
        for doc in query:
            data = doc.to_dict()
            docent_ids = data.get("docent_ids", [])
            max_docents = data.get("max_docents", 1)
            
            # Legacy migration protection
            legacy_docent = data.get("docent_id")
            if legacy_docent and legacy_docent not in docent_ids:
                docent_ids.append(legacy_docent)
                
            if payload.docent_id in docent_ids:
                continue # Already has it
                
            # NEW: Specialty restriction check
            allowed_espc = data.get("especialitats_permises", [])
            if allowed_espc:
                # Need to find docent's specialty. We'll fetch it if not cached.
                # For efficiency, we assume the frontend checked it, but backend MUST verify.
                docent_doc = db.collection("usuaris").document(payload.docent_id).get()
                if docent_doc.exists:
                    d_data = docent_doc.to_dict()
                    d_espc = d_data.get("especialitats", [])
                    # If user is ADMIN, they can take anything? Or if no specialty overlaps?
                    if d_data.get("rol") != "ADMIN" and not any(e in allowed_espc for e in d_espc):
                        raise HTTPException(status_code=403, detail=f"Aquesta franja està reservada per a: {', '.join(allowed_espc)}")
            
            batch.update(doc.reference, {"docent_ids": firestore.ArrayUnion([payload.docent_id])})
            updated_slots.append(doc.id)
            
        if not updated_slots:
            raise HTTPException(status_code=404, detail="No s'han trobat franges o ja estan plenes")
            
        batch.commit()
        
        await manager.broadcast({
            "type": "MODULE_TAKEN",
            "docent_id": payload.docent_id,
            "modul_id": payload.modul_id,
            "grup_id": payload.grup_id,
            "slots": updated_slots
        })
        return {"status": "success", "slots_updated": len(updated_slots)}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tria/release")
async def release_modul(payload: SlotSelection):
    try:
        if not db: return {"status": "success"}
        horaris_ref = db.collection("horaris")
        query = horaris_ref.where("modul_id", "==", payload.modul_id)\
                           .where("grup_id", "==", payload.grup_id).stream()
                           
        batch = db.batch()
        updated_slots = []
        for doc in query:
            data = doc.to_dict()
            docent_ids = data.get("docent_ids", [])
            legacy_docent = data.get("docent_id")
            
            if payload.docent_id in docent_ids or legacy_docent == payload.docent_id:
                batch.update(doc.reference, {"docent_ids": firestore.ArrayRemove([payload.docent_id])})
                # Auto cleanup legacy if releasing it
                if legacy_docent == payload.docent_id:
                    batch.update(doc.reference, {"docent_id": firestore.DELETE_FIELD})
                updated_slots.append(doc.id)
            
        if updated_slots:
            batch.commit()
        
        await manager.broadcast({
            "type": "MODULE_RELEASED",
            "docent_id": payload.docent_id,
            "modul_id": payload.modul_id,
            "grup_id": payload.grup_id,
            "slots": updated_slots
        })
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -- Càrrecs i Guàrdies --

class ExtraHourPayload(BaseModel):
    docent_id: str
    tipus: str # "CARREC" o "GUARDIA"
    quantitat: int
    nom: str # Ej: "Cap de Departament", "Guàrdia Pati"

@app.post("/tria/extra")
async def add_extra_hour(payload: ExtraHourPayload):
    try:
        if not db: return {"status": "success"}
        # Create virtual slots
        extra_ref = db.collection("tria_extres")
        ids = []
        batch = db.batch()
        for i in range(payload.quantitat):
            new_doc = extra_ref.document()
            batch.set(new_doc, {
                "docent_id": payload.docent_id,
                "tipus": payload.tipus,
                "nom": payload.nom
            })
            ids.append(new_doc.id)
        batch.commit()
        
        await manager.broadcast({
            "type": "EXTRA_ADDED",
            "docent_id": payload.docent_id,
            "tipus": payload.tipus,
            "quantitat": payload.quantitat
        })
        return {"status": "success", "added": len(ids)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tria/extra/{docent_id}")
def get_extra_hours(docent_id: str):
    try:
        if not db: return []
        docs = db.collection("tria_extres").where("docent_id", "==", docent_id).stream()
        return [{"id": d.id, **d.to_dict()} for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -- Administració (Cap d'Estudis) --

class StateUpdatePayload(BaseModel):
    ordre: List[str]
    fase: str
    torn_actual: Optional[str] = None

@app.put("/tria/admin/state/{especialitat}")
async def override_state(especialitat: str, payload: StateUpdatePayload):
    try:
        if not db: return {"status": "success"}
        db.collection("tria").document(especialitat).set(payload.dict())
        
        await manager.broadcast({
            "type": "STATE_OVERRIDDEN",
            "especialitat": especialitat,
            "torn_actual": payload.torn_actual,
            "ordre": payload.ordre
        })
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class RenamePayload(BaseModel):
    new_name: str

@app.patch("/tria/admin/rename/{old_name}")
async def rename_specialty(old_name: str, payload: RenamePayload):
    try:
        if not db: return {"status": "success"}
        new_name = payload.new_name.strip()
        if not new_name:
            raise HTTPException(status_code=400, detail="El nou nom no pot estar buit")
        if old_name == new_name:
            return {"status": "success", "message": "Nom idèntic, res a fer"}

        # Copy tria state to new document
        old_doc = db.collection("tria").document(old_name).get()
        if not old_doc.exists:
            raise HTTPException(status_code=404, detail=f"Especialitat '{old_name}' no trobada")
        db.collection("tria").document(new_name).set(old_doc.to_dict())
        db.collection("tria").document(old_name).delete()

        # Update all users that reference old_name in their especialitats list
        users = db.collection("usuaris").stream()
        batch = db.batch()
        for user_doc in users:
            user_data = user_doc.to_dict()
            especialitats = user_data.get("especialitats", [])
            if old_name in especialitats:
                new_list = [new_name if e == old_name else e for e in especialitats]
                batch.update(user_doc.reference, {"especialitats": new_list})
        batch.commit()

        await manager.broadcast({
            "type": "SPECIALTY_RENAMED",
            "old_name": old_name,
            "new_name": new_name
        })
        return {"status": "success", "old_name": old_name, "new_name": new_name}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class AvailabilityUpdate(BaseModel):
    docent_id: str
    x_slots: List[str]

@app.post("/tria/availability")
async def update_availability(payload: AvailabilityUpdate):
    try:
        if not db: return {"status": "success"}
        db.collection("tria_disponibilitat").document(payload.docent_id).set({
            "x_slots": payload.x_slots
        })
        await manager.broadcast({
            "type": "AVAILABILITY_UPDATED",
            "docent_id": payload.docent_id,
            "slots": payload.x_slots
        })
        return {"status": "success"}
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

@app.get("/tria/availability/{docent_id}")
def get_availability(docent_id: str):
    try:
        if not db: return []
        doc = db.collection("tria_disponibilitat").document(docent_id).get()
        if doc.exists: return doc.to_dict().get("x_slots", [])
        return []
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

@app.post("/tria/next_turn/{especialitat}")
async def next_turn(especialitat: str):
    try:
        if not db: return {"status": "success"}
        state_ref = db.collection("tria").document(especialitat)
        doc = state_ref.get()
        if not doc.exists: raise HTTPException(status_code=400, detail="Estat no inicialitzat")
        
        data = doc.to_dict()
        ordre = data.get("ordre", [])
        actual = data.get("torn_actual")
        
        if not ordre: return {"status": "done"}
            
        if not actual:
            next_docent = ordre[0]
        else:
            try:
                idx = ordre.index(actual)
                if idx + 1 < len(ordre): next_docent = ordre[idx+1]
                else: next_docent = None
            except ValueError:
                next_docent = ordre[0]
                
        state_ref.update({"torn_actual": next_docent})
        
        await manager.broadcast({
            "type": "TURN_CHANGED",
            "especialitat": especialitat,
            "torn_actual": next_docent
        })
        return {"status": "success", "torn_actual": next_docent}
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

class SetTurnPayload(BaseModel):
    torn_actual: Optional[str]

@app.post("/tria/set_turn/{especialitat}")
async def set_turn(especialitat: str, payload: SetTurnPayload):
    try:
        if not db: return {"status": "success"}
        state_ref = db.collection("tria").document(especialitat)
        state_ref.update({"torn_actual": payload.torn_actual})
        
        await manager.broadcast({
            "type": "TURN_CHANGED",
            "especialitat": especialitat,
            "torn_actual": payload.torn_actual
        })
        return {"status": "success"}
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

@app.get("/horaris/")
def get_horaris():
    try:
        if not db: return []
        docs = db.collection("horaris").stream()
        result = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            result.append(data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SlotMovePayload(BaseModel):
    dia_setmana: int
    hora_inici: str
    hora_fi: str
    modul_nom: str = None
    max_docents: int = 1
    especialitats_permises: Optional[List[str]] = None

@app.put("/horaris/{slot_id}")
async def update_horari_slot(slot_id: str, payload: SlotMovePayload):
    try:
        if not db: return {"status": "success"}
        doc_ref = db.collection("horaris").document(slot_id)
        if not doc_ref.get().exists:
            raise HTTPException(status_code=404, detail="Franja no trobada")
            
        updates = {
            "dia_setmana": payload.dia_setmana,
            "hora_inici": payload.hora_inici,
            "hora_fi": payload.hora_fi,
            "max_docents": payload.max_docents
        }
        if payload.modul_nom is not None:
            updates["modul_nom"] = payload.modul_nom
        if payload.especialitats_permises is not None:
            updates["especialitats_permises"] = payload.especialitats_permises
            
        doc_ref.update(updates)
        
        await manager.broadcast({"type": "SCHEDULE_SHIFTED"})
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SlotCreatePayload(BaseModel):
    grup_id: str
    dia_setmana: int
    hora_inici: str
    hora_fi: str
    modul_nom: str
    max_docents: int = 1
    especialitats_permises: List[str] = []
    
@app.post("/horaris/")
async def create_horari_slot(payload: SlotCreatePayload):
    try:
        if not db: return {"status": "success", "id": "fake"}
        new_ref = db.collection("horaris").document()
        new_ref.set({
            "grup_id": payload.grup_id,
            "grup_nom": payload.grup_id,
            "dia_setmana": payload.dia_setmana,
            "hora_inici": payload.hora_inici,
            "hora_fi": payload.hora_fi,
            "modul_nom": payload.modul_nom,
            "modul_id": payload.modul_nom,
            "max_docents": payload.max_docents,
            "especialitats_permises": payload.especialitats_permises,
            "docent_ids": []
        })
        await manager.broadcast({"type": "SCHEDULE_SHIFTED"})
        return {"status": "success", "id": new_ref.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/horaris/{slot_id}")
async def delete_horari_slot(slot_id: str):
    try:
        if not db: return {"status": "success"}
        db.collection("horaris").document(slot_id).delete()
        await manager.broadcast({"type": "SCHEDULE_SHIFTED"})
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
