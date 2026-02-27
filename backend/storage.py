import json
import os
from pathlib import Path
from typing import List
from backend.schemas import Vote, SystemMetadata
from datetime import datetime

FILE_PATH = "votes.json"
FILE_METADATA = "votesMetadata.json"

def load_votes() -> List[Vote]:
    """
    The 'Thaw' function. Dezghetarea
    It reads the JSON and turns every dictionary into a Vote Object.
    """
    if not os.path.exists(FILE_PATH):
        return []

    with open(FILE_PATH, "r") as f:
        try:
            raw_data = json.load(f)
            # This is the magic line: it converts dict -> Vote object
            # The **item 'pours' the dictionary keys into the Vote class
            return [Vote(**item) for item in raw_data]
        except (json.JSONDecodeError, TypeError):
            # If the file is messy or empty, return an empty list
            return []
        
def get_next_id() -> int:
    #we need an initialization of the id before opening the json file
    current_meta = SystemMetadata(last_id=0)

    #tot ce ii in if-ul asta e sa verificam daca id ul exista in fisierul json
    #daca exista stim care e actualul id
    if os.path.exists(FILE_METADATA) and os.path.getsize(FILE_METADATA) > 0:
        with open(FILE_METADATA, "r") as f:
            try:
                #we open the josn file
                data = json.load(f)
                current_meta = SystemMetadata(**data) # trabsformam json file in obeject folosind cele doua **
            except json.JSONDecodeError:
                # If the file is corrupted/empty, we stick with the default (0)
                pass
    new_id = current_meta.last_id + 1
    current_meta.last_id = new_id

    # 3. Write it back (This creates the file if it's missing!)
    with open(FILE_METADATA, "w") as f:
        json.dump(current_meta.model_dump(), f, indent=4) # cu dump il facem din obiect in json file inapoi
    return new_id
    

def save_votes(votes_dict: List[dict]) -> None: 
    if votes_dict is None:
        return
    with open(FILE_PATH, "w") as f:
        json.dump(votes_dict, f, indent=4) # 'indent' makes the JSON file readable for humans!

def rename_player(old_name: str, new_name: str) -> int:
    """
    Example of using the objects to update data.
    """
    votes = load_votes() # Now 'votes' is a list of Vote OBJECTS
    count = 0
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for v in votes:
        if v.name == old_name:
            v.name = new_name
            v.modified_at = now
            count += 1
            
    
    if count > 0:
        # We must turn objects back to dicts before saving!
        save_votes([v.model_dump() for v in votes])
    return count

def deactivate_player_vote(vote_id: int) -> bool:
    all_votes = load_votes()
    found = False

    for v in all_votes:
        if v.id == vote_id:
            v.is_active = False # The "Action": Flip the switch
            found = True
            break # We found it, no need to keep looking!

    if found:
        # We save the WHOLE list, including the deactivated item
        save_votes([v.model_dump() for v in all_votes])
    
    return found
