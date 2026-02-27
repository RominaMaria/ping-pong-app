from backend.leaderboard import enhanced_leaderBoard_plus_summary


#Test 1
def test_percentage_100_when_one_vote():
    votes = [
        {"name":"Romina", "day":["Monday"]}
    ]
    
    result = enhanced_leaderBoard_plus_summary(votes)

    # Check winner
    winner = result["winner"]
    assert winner["winning_days"] == ["Monday"] 
    assert winner["winning_count"] == 1
    assert winner["players"] == {'Monday': ['Romina']}
    
    # Check leaderboard
    leaderboard = result["leaderboard"]
    assert len(leaderboard) == 1
    assert leaderboard[0]["day"] == "Monday"
    assert leaderboard[0]["votes"] == 1
    assert leaderboard[0]["players"] == ['Romina']
    assert leaderboard[0]["percent"] == 100.0

def test_50_percentage_when_2_votes():
    votes = [
        {"name":"Romina", "day":["Monday"]},
        {"name":"Alex", "day":["Tuesday"]},
        
    ]
    result = enhanced_leaderBoard_plus_summary(votes)

    leaderboard = result["leaderboard"]
    winner = result["winner"]
    assert leaderboard[0]["percent"] == 50.0
    assert leaderboard[1]["percent"] == 50.0
    assert winner["winning_days"] == ['Monday', 'Tuesday']

def test_enhanced_leaderboard_no_votes():
    assert enhanced_leaderBoard_plus_summary([]) == None


def test_winner_tie():
    votes = [
        {"name": "Romina", "day": ["Monday"]},
        {"name": "Alex", "day": ["Tuesday"]},
    ]

    result = enhanced_leaderBoard_plus_summary(votes)

    assert result["winner"]["winning_count"] == 1
    assert result["winner"]["winning_days"] == ['Monday', 'Tuesday']


def test_leaderboard_sorted():
    votes = [
        {"name": "Romina", "day": ["Monday"]},
        {"name": "Alex", "day": ["Tuesday"]},
        {"name": "Maria", "day": ["Monday"]},
    ]
    result = enhanced_leaderBoard_plus_summary(votes)
    leaderboard  = result["leaderboard"]
    assert leaderboard[0]["votes"] >= leaderboard[1]["votes"]


def test_players_group_correctly():
    votes = [
        {"name": "Romina", "day": ["Monday"]},
        {"name": "Alex", "day": ["Monday"]},
        {"name": "Maria", "day": ["Wednesday"]},
    ]
    result = enhanced_leaderBoard_plus_summary(votes)
    monday = next(day for day in result["leaderboard"] if day["day"] == "Monday")
    assert set(monday["players"]) == {"Romina","Alex"}

def test_function_does_not_crash_with_weird_data():
    votes = [
        {"name": "", "day": ["Monday"]},
        {"name": None, "day": ["Monday"]},
    ]

    result = enhanced_leaderBoard_plus_summary(votes)
    winner = result["winner"]
    winner["winning_days"] == ["Monday"]
    winner["winning_count"] == 2
    winner["players"] == {}  # no valid names
    winner["percent"] == 100.0

def test_no_votes_returns_none():
    votes = []
    result = enhanced_leaderBoard_plus_summary(votes)
    assert result is None

