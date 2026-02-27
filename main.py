from fastapi import FastAPI, HTTPException
from backend.storage import load_votes, save_votes, rename_player, deactivate_player_vote, get_next_id
from backend.leaderboard import enhanced_leaderBoard_plus_summary, user_votes, count_hourly_activity, build_text_chart, collect_all_notes
from backend.schemas import VoteCreate, Vote
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from collections import Counter

app = FastAPI()

# This tells FastAPI: "It's okay to let the Frontend talk to me"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, we'd be more specific
    allow_methods=["*"],
    allow_headers=["*"],
)
votes = load_votes() #Memory (votes variable) → for performance and API

@app.post("/vote")
def add_vote(request: VoteCreate):
    try:
        # 1. Load existing data
        all_votes = load_votes() 
        
        # --- NEW: DUPLICATE CHECK ---
        for existing_vote in all_votes: # existing vote is form the json file and the request vote is from the user frontend
            # Check if name exists (ignoring case) AND is currently active
            if existing_vote.name.lower() == request.name.lower() and existing_vote.is_active:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Player '{request.name}' has already voted!"
                )
        # ----------------------------

        # 2. Get the Next ID and Timestamp
        new_id = get_next_id()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 3. Create the new Vote object
        new_entry = Vote(id=new_id, created_at=now, **request.model_dump())
        
        # 4. Add and Save
        all_votes.append(new_entry)
        
        # Convert objects back to dicts for the JSON file
        dict_list = [v.model_dump() for v in all_votes]
        save_votes(dict_list)
        
        return new_entry

    except HTTPException as http_e:
        # Re-raise HTTP errors so they reach the Frontend properly
        raise http_e
    except Exception as e:
        print(f"CRASH LOG: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
#Delete all votes (reset system)
@app.delete("/votes")
def clear_votes():
    votes.clear()          # clear memory
    save_votes([])    
    return {"status": "cleared"}


@app.get("/leaderboard")
def get_leaderboard():
    all_votes = load_votes()
    active_votes = [v for v in all_votes if v.is_active]
    return {
        "by_day": enhanced_leaderBoard_plus_summary(active_votes),
        "by_user": user_votes(active_votes),
        "all_notes": collect_all_notes(active_votes)
    }


@app.put("/players/rename/{old_name}/{new_name}")
def rename_player_endpoit(old_name:str, new_name:str):
    changed_count = rename_player(old_name, new_name)

    if changed_count == 0:
        raise HTTPException(status_code=404, detail=f"Player {old_name} not found")
    return{"message": f"Successfuly updated {changed_count} votes to {new_name}"}

@app.delete("/players/deactivate/{vote_id}")
def deactivate_player_vote_player_endpoint(vote_id: int):
    count = deactivate_player_vote(vote_id)
    if count == 0:
        raise HTTPException(status_code=404, detail=f"Player {vote_id} not found")
    return{"message": f"Successfuly deactivated vote"}

@app.get("/votes/recent")
def get_recent_votes(limit: int = 10):
    all_votes = load_votes()
    active_votes = [v for v in all_votes if v.is_active]

    sorted_votes = sorted(active_votes, key=lambda x: x.created_at or x.modified_at or x.id, reverse= True)

    return sorted_votes[:limit]

@app.get("/votes/stats/chart")
def get_visual_stats():
    all_votes = load_votes()
    active_only = [v for v in all_votes if v.is_active]
    
    # 1. Get the numbers
    stats = count_hourly_activity(active_only)
    
    # 2. Sort the hours so the chart goes from 00:00 to 23:00
    sorted_hours = dict(sorted(stats.items()))
    
    # 3. Build the visual bars
    visual_chart = build_text_chart(sorted_hours)
    
    return {
        "title": "Hourly Activity Heatmap",
        "chart": visual_chart
    }
    
@app.get("/votes/stats")
def get_vote_stats():
    all_votes = load_votes()
    # Filter only active votes
    active_days = []
    for v in all_votes:
        if v.is_active and v.day:
            # Since 'day' is a list [day], we take the first element
            active_days.extend(v.day)
    
    # Counter turns ['Mon', 'Mon', 'Tue'] into {'Mon': 2, 'Tue': 1}
    stats = Counter(active_days)
    return stats

@app.get("/votes/notes")
def list_notes():
    all_votes = load_votes()
    all_notes = []
    for v in all_votes:
        if v.is_active and v.note:
            all_notes.append(v.note)
    return all_notes