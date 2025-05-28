import os  
import traceback
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from models import Base, Contact
from schemas import IdentifyIn, IdentifyOut

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/identify", response_model=IdentifyOut)
def identify(payload: IdentifyIn, request: Request):
    session = SessionLocal()
    try:
        # Step 1: Fetch existing contacts by email or phone
        matches = session.query(Contact).filter(
            or_(
                Contact.email == payload.email,
                Contact.phoneNumber == payload.phoneNumber
            )
        ).all()

        # Step 2: Insert if no match found
        if not matches:
            new = Contact(email=payload.email, phoneNumber=payload.phoneNumber)
            session.add(new)
            session.commit()
            matches = [new]
        else:
            # Check for partial match
            known_emails = {c.email for c in matches if c.email}
            known_phones = {c.phoneNumber for c in matches if c.phoneNumber}
            if payload.email not in known_emails or payload.phoneNumber not in known_phones:
                primary_id = matches[0].linkedId if matches[0].linkedId else matches[0].id
                new_secondary = Contact(
                    email=payload.email,
                    phoneNumber=payload.phoneNumber,
                    linkedId=primary_id,
                    linkPrecedence='secondary'
                )
                session.add(new_secondary)
                session.commit()
                matches.append(new_secondary)

        # Step 3: BFS traversal to get full linked contact group
        group = set(matches)
        queue = list(matches)
        while queue:
            current = queue.pop()
            secondaries = getattr(current, "secondaries", None)
            if secondaries and isinstance(secondaries, list):
                for sec in secondaries:
                    if sec not in group:
                        group.add(sec)
                        queue.append(sec)
            if current.linkedId:
                parent = session.get(Contact, current.linkedId)
                if parent and parent not in group:
                    group.add(parent)
                    queue.append(parent)

        # Step 4: Identify primary contact
        primaries = [c for c in group if c.linkPrecedence == 'primary']
        primary = min(primaries, key=lambda c: c.createdAt)

        # Step 5: Normalize all contacts in the group
        for contact in group:
            if contact.id != primary.id:
                contact.linkPrecedence = 'secondary'
                contact.linkedId = primary.id
        session.commit()

        # Step 6: Re-fetch updated contacts fully
        final_group = session.query(Contact).filter(
            or_(
                Contact.id == primary.id,
                Contact.linkedId == primary.id
            )
        ).all()

        return {
            "contact": {
                "primaryContactId": primary.id,
                "emails": sorted({c.email for c in final_group if c.email}),
                "phoneNumbers": sorted({c.phoneNumber for c in final_group if c.phoneNumber}),
                "secondaryContactIds": sorted([c.id for c in final_group if c.id != primary.id])
            }
        }

    except Exception:
        print("\n--- INTERNAL SERVER ERROR ---")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        session.close()


@app.get("/")
def read_root():
    return RedirectResponse(url="/docs")
