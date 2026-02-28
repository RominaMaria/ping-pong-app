import { useState, useEffect } from 'react'
import axios from 'axios'
import VoteForm from './VoteForm' // 1. We import your new component

function App() {
  const [votes, setVotes] = useState([])
  const API_BASE_URL = "https://ping-pong-app.onrender.com";
  // 2. This is the function we will give to the VoteForm
  const fetchVotes = async () => {
    try {
      // Adding ?t=... makes the URL unique so the browser doesn't use a "saved" version
      const response = await axios.get(`${API_BASE_URL}/votes/recent?t=${Date.now()}`)
      
      // We sort them so the newest (highest ID or latest time) is at the TOP
      const sortedData = response.data.sort((a, b) => b.id - a.id)
      
      setVotes(sortedData)
      console.log("UI Updated with", sortedData.length, "votes")
    } catch (error) {
      console.error("Backend connection failed", error)
    }
  };

  const [stats, setStats] = useState({})
  const fetchStats = async() => {
    try{
      const response = await axios.get(`${API_BASE_URL}/votes/stats`);
      
      setStats(response.data);
    } catch (error){
      console.log("Error fetching stats", error)
    }
  };

  const [notes, setNotes] = useState([])
  const fetchNotes = async() => {
    try{
      const response = await axios.get(`${API_BASE_URL}/votes/notes`);
      const cleanNotes = response.data.filter(n => n !== null && n !== "")
      const sortedNotes = cleanNotes.data.sort((a,b) => b.length - a.length)
      setNotes(sortedNotes);
    } catch (error){
      console.log("Error fetching the notes", error)
    }
  };

  const deactivatePlayer = async (vote_id) => {
    try {
      await axios.delete(`${API_BASE_URL}/players/deactivate/${vote_id}`);
      refreshAllData(); // <--- This makes the name vanish from the screen!
    } catch (error) {
      alert(error.response?.data?.detail || "Delete failed");
    }
  };

  const handleRename = async (oldName) => {
  const newName = window.prompt(`Rename "${oldName}" to:`, oldName);
  
  // If user didn't click cancel and typed something
  if (newName && newName !== oldName) {
    try {
      // Notice: old_name is in the PATH, new_name is a QUERY (?new_name=...)
      await axios.put(`${API_BASE_URL}/players/rename/${oldName}/${newName}`);
      refreshAllData();
    } catch (error) {
      alert(error.response?.data?.detail || "Rename failed");
    }
  }
  };

  // 3. Run fetchVotes once when the page first loads
  useEffect(() => {
    fetchVotes();
    fetchStats();
    fetchNotes();
  }, [])

  const refreshAllData = ()  =>{
    fetchVotes();
    fetchStats();
    fetchNotes();
  };

  const resume = [...new Set(votes.map(v => v.name))]. join(", ")

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px', fontFamily: 'Arial' }}>
      <h1>🏓 Ping-Pong Portal</h1>
      
      {/* 4. We use the component and pass the 'fetchVotes' function as a Prop */}
      <VoteForm onVoteSuccess={refreshAllData} />

      <hr />
    <div style={{ background: '#f9f9f9', padding: '20px', borderRadius: '10px' }}>
      <div style={{
        borderTop: '1px solid #eee',
        padding: '15px 0',
        fontSize: '14px',
        color: '#777'
      }}>
      <span >
      <h2>Already voted: {resume}</h2>
      </span>
      </div>
    <h2>Live Distribution</h2>
      {Object.entries(stats).map(([day, count]) => (
        <div key={day} style={{ marginBottom: '10px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>{day}</span>
            <span>{count} votes</span>
          </div>
          {/* This div acts as the bar of the chart */}
          <div style={{ 
            background: '#007bff', 
            height: '20px', 
            width: `${count * 20}px`, // Simple math: 20 pixels per vote
            borderRadius: '5px',
            transition: 'width 0.5s ease' 
          }} />
        </div>
      ))}
    </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <h2>Notes</h2>
        {/* 'notes' is a list, so we map it directly */}
        {notes.map((noteText, index) => (
          <div key={index} style={{ borderLeft: '4px solid #007bff', paddingLeft: '10px', marginBottom: '10px' }}>
            <p style={{ margin: 0 }}>{noteText}</p>
          </div>
        ))}
      </div>
      <h2>Recent Votes</h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {votes.map((v) => (
          <div 
            key={v.id} 
            style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center', 
              padding: '15px', 
              marginBottom: '10px',
              border: '1px solid #ddd', 
              borderRadius: '8px',
              backgroundColor: '#fff'
            }}
          >
            {/* --- LEFT SIDE: THE INFO COLUMN --- */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
              <div>
                <strong style={{ fontSize: '1.1rem' }}>{v.name}</strong> 
                <span style={{ color: '#666', marginLeft: '10px' }}>
                  playing on {v.day.join(', ')}
                </span>
              </div>
              
              {/* Show the note only if it exists */}
              {v.note && (
                <p style={{ 
                  margin: 0, 
                  fontStyle: 'italic', 
                  color: '#555555', 
                  fontSize: '0.9rem',
                  borderLeft: '3px solid #007bff',
                  paddingLeft: '10px'
                }}>
                  "{v.note}"
                </p>
              )}
            </div>

            {/* --- RIGHT SIDE: THE ACTION --- */}
            <button 
              onClick={() => deactivatePlayer(v.id)} 
              style={{ 
                backgroundColor: '#ff4d4f', 
                color: 'white', 
                border: 'none', 
                padding: '8px 12px', 
                borderRadius: '5px', 
                cursor: 'pointer',
                fontWeight: 'bold'
              }}
            >
              Deactivate
            </button>
            <button 
            onClick={() => handleRename(v.name)}
            style={{ 
              marginRight: '10px', 
              backgroundColor: '#f0ad4e', 
              color: 'white', 
              border: 'none', 
              padding: '5px', 
              borderRadius: '4px' }}
          >
            Rename ✏️
          </button>
          </div>
        ))}
      </div>
      
    </div>
    
  )
}

export default App