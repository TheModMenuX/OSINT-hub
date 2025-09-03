from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import whois
import requests
import socket
import dns.resolver
from typing import List, Optional
import datetime

app = FastAPI()

class DomainInfo(BaseModel):
    domain: str
    registrar: Optional[str]
    creation_date: Optional[datetime.datetime]
    expiration_date: Optional[datetime.datetime]
    nameservers: List[str]

@app.get("/api/domain/{domain}", response_model=DomainInfo)
async def get_domain_info(domain: str):
    try:
        w = whois.whois(domain)
        return DomainInfo(
            domain=domain,
            registrar=w.registrar,
            creation_date=w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date,
            expiration_date=w.expiration_date[0] if isinstance(w.expiration_date, list) else w.expiration_date,
            nameservers=w.name_servers
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))