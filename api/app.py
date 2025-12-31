from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
import sqlite3
from pydantic import BaseModel
from auth import login, get_current_user, User

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def db():
    conn = sqlite3.connect("rules.db")
    conn.execute("CREATE TABLE IF NOT EXISTS rules (id INTEGER PRIMARY KEY, domain TEXT UNIQUE)")
    return conn

class Rule(BaseModel):
    domain: str

@app.post("/login")
def do_login(form_data: OAuth2PasswordRequestForm = Depends()):
    return login(form_data)

@app.get("/rules", response_model=List[Rule])
def list_rules(user: User = Depends(get_current_user)):
    conn = db()
    cur = conn.execute("SELECT domain FROM rules ORDER BY domain")
    rows = [Rule(domain=r[0]) for r in cur.fetchall()]
    conn.close()
    return rows

@app.post("/rules", response_model=Rule)
def add_rule(rule: Rule, user: User = Depends(get_current_user)):
    conn = db()
    try:
        conn.execute("INSERT INTO rules(domain) VALUES (?)", (rule.domain,))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=409, detail="Rule already exists")
    conn.close()
    return rule

@app.delete("/rules/{domain}")
def delete_rule(domain: str, user: User = Depends(get_current_user)):
    conn = db()
    cur = conn.execute("DELETE FROM rules WHERE domain = ?", (domain,))
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"deleted": domain}
