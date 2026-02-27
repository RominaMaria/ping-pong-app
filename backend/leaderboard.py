
from typing import List, Dict, Optional, Union, TypedDict
from backend.schemas import Vote

class Winner(TypedDict):
    winning_days: List[str]
    winning_count: int
    players: Dict[str, List[str]]
    percent : float

class LeaderboardRow(TypedDict):
    day : str
    votes: int
    players: List[str]
    percent: float

class EnhancedResult(TypedDict):
    winner: Winner
    leaderboard: List[LeaderboardRow]

class Board(TypedDict):
    day_count: Dict[str, int]
    players: Dict[str, List[str]]
    total_votes: int

class UserVote(TypedDict):
    vote_count: str
    days: List[str]
    percent: float

VALID_DAYS = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday"}

def percent(count: int, total: int) -> float:
    return 0.0 if total == 0 else round((count/ total)*100 , 1)

def count_votes(
    votes: List[Vote]
) -> Dict[str, int]:
    
    count: Dict[str, int] = {}
    for entry in votes:
        days = entry.day
        for day in days:
            count[day] = count.get(day, 0) + 1
    return count


def group_players(
    votes: List[Vote]
) -> Dict[str, List[str]]:
    
    players: Dict[str, List[str]] = {}

    for entry in votes:
        name = entry.name
        for day in entry.day:
            current_players = players.get(day, [])
            current_players.append(name)
            players[day] = current_players
    return players


def build_winner(
    board: Board
)-> Winner:
    winning_days: List[str] = []
    
    if not board["day_count"]:
        return {
        "winning_days": [],
        "winning_count": 0,
        "players": {},
        "percent": 0.0
    }
    max_votes = max(board["day_count"].values())

    winning_days = [day for day, count in board["day_count"].items() if count == max_votes]

    players = {day: board["players"].get(day, []) for day in winning_days}

    percent_value = percent(max_votes, board["total_votes"])
    return {
        "winning_days": winning_days,
        "winning_count": max_votes,
        "players": players,
        "percent": percent_value
    }

def build_leaderBoard(
    board: Board
)-> List[LeaderboardRow]:
    
    leaderBoard: List[LeaderboardRow] = []
    for day, count in board["day_count"].items():
        percent_value = percent(count, board["total_votes"])
        valid_players = [
            name for name in board["players"].get(day, [])
            if name and name.strip()
        ]
        if not board["players"].get(day):
            print(f"Warning: no valid players for day {day}")
        leaderBoard.append({
            "day": day, 
            "votes": count, 
            "players": sorted(valid_players), 
            "percent": percent_value
        })
    
    return sorted(leaderBoard, key=lambda x: (-x["votes"], x["day"]))

def enhanced_leaderBoard_plus_summary(
    votes: List[Vote]
) -> Optional[EnhancedResult]:

    if not votes:
        return None
    active_votes = [v for v in votes if v.is_active]

    board: Board = {
        "day_count": count_votes(active_votes),
        "players": group_players(active_votes),
        "total_votes": sum(len(v.day) for v in active_votes)
    }

    

    return {
        "winner": build_winner(board),
        "leaderboard": build_leaderBoard(board),
    }

def user_votes(votes: List[Vote]) -> Dict[str, UserVote]:
    users = {}
    for entry in votes:
        name = entry.name
        # 1. Use .get() to find the user, or provide a fresh starting template
        # This replaces all the "if name not in users" logic!
        user_stats = users.get(name, {
            "vote_count": 0,
            "days": [],
            "percent": 0.0
        })
        user_stats["vote_count"] += len(entry.day)
        for day in entry.day:
            if day not in user_stats["days"]:
                user_stats["days"].append(day)
        # 3. Save it back into the container
        users[name] = user_stats
    total_votes = 0
    for user in users.values():
        total_votes += user["vote_count"]

    # ---- calculate percent ----
    for user_summary in users.values():
        if total_votes == 0:
            user_summary["percent"] = 0.0
        else:
            user_summary["percent"] = (
                user_summary["vote_count"] / total_votes
            ) * 100

    return users

def count_hourly_activity(votes: List[Vote]) -> Dict[str, int]:
    hourly_counts = {}
    for entry in votes:
        hour = entry.created_at[11:13]

        # This one line does everything:
        # 1. Tries to find the hour
        # 2. If not found, starts at 0
        # 3. Adds 1
        hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
    return hourly_counts

def build_text_chart(stats: Dict[str, int]) -> Dict[str, str]:
    chart = {}
    # We loop through our hours and counts
    for hour, count in stats.items():
        # We transform the number 3 into "###"
        chart[hour] = "🏓" * count 
    return chart

def collect_all_notes(votes: List[Vote]) -> List[str]:
    return[v for v in votes if v.note]

