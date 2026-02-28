from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()


# Модель для создания и обновления (без id)
class SessionCreate(BaseModel):
    name: str
    ip: str


# Полная модель (с id)
class Session(SessionCreate):
    id: int


# In-memory хранилище
sessions: List[Session] = []
current_id = 1


# CREATE
@app.post("/sessions", response_model=Session, status_code=201)
def create_session(session: SessionCreate):
    global current_id

    new_session = Session(
        id=current_id,
        name=session.name,
        ip=session.ip
    )

    sessions.append(new_session)
    current_id += 1

    return new_session


# READ ALL
@app.get("/sessions", response_model=List[Session])
def get_sessions():
    return sessions


# READ ONE
@app.get("/sessions/{id}", response_model=Session)
def get_session(id: int):
    for session in sessions:
        if session.id == id:
            return session
    raise HTTPException(status_code=404, detail="Session not found")


# UPDATE (PUT — полная замена)
@app.put("/sessions/{id}", response_model=Session)
def update_session(id: int, updated: SessionCreate):
    for index, session in enumerate(sessions):
        if session.id == id:
            new_session = Session(
                id=id,
                name=updated.name,
                ip=updated.ip
            )
            sessions[index] = new_session
            return new_session

    raise HTTPException(status_code=404, detail="Session not found")


# DELETE
@app.delete("/sessions/{id}", status_code=204)
def delete_session(id: int):
    for index, session in enumerate(sessions):
        if session.id == id:
            sessions.pop(index)
            return

    raise HTTPException(status_code=404, detail="Session not found")