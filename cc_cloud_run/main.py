from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from google.cloud import firestore
from typing import Annotated
import datetime

app = FastAPI()

# mount static files
app.mount("/static", StaticFiles(directory="/app/static"), name="static")
templates = Jinja2Templates(directory="/app/template")

# init firestore client
db = firestore.Client()
votes_collection = db.collection("votes")


@app.get("/")
async def read_root(request: Request):
    # ====================================
    # ++++ START CODE HERE ++++
    # ====================================

    # stream all votes; count tabs / spaces votes, and get recent votes
    votes = votes_collection.stream()

    tabs_count = 0
    spaces_count = 0
    vote_data = []
    for v in votes:
        vote = v.to_dict()
        vote_data.append(vote)
        if vote.get('team') == "SPACES":
            spaces_count += 1
        else:
            tabs_count += 1

    sorted_votes = sorted(vote_data, key=lambda vote: vote['time_cast'], reverse=True)

    # ====================================
    # ++++ STOP CODE ++++
    # ====================================
    return templates.TemplateResponse("index.html", {
        "request": request,
        "tabs_count": tabs_count,
        "spaces_count": spaces_count,
        "recent_votes": sorted_votes
    })


@app.post("/")
async def create_vote(team: Annotated[str, Form()]):
    if team not in ["TABS", "SPACES"]:
        raise HTTPException(status_code=400, detail="Invalid vote")

    # ====================================
    # ++++ START CODE HERE ++++
    # ====================================

    # create a new vote document in firestore
    votes_collection.add({
        "team": team,
        "time_cast": datetime.datetime.now(datetime.timezone.utc).isoformat()
    })

    return JSONResponse(status_code=200, content={"message": "Vote recorded successfully"})

    # ====================================
    # ++++ STOP CODE ++++
    # ====================================
