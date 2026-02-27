import { useState } from 'react'
import axios from 'axios'

function VoteForm({ onVoteSuccess }) {
  const API_BASE_URL = "https://ping-pong-app.onrender.com";
  // Memory for the form
  const [name, setName] = useState('')
  const [note, setNote] = useState('')
  const [selectedDays, setSelectedDays] = useState([])

  const [loading, setLoading] = useState(false) // New state
  
  const handleDayChange = (day) => {
    if (selectedDays.includes(day)){
      setSelectedDays(selectedDays.filter(d => d !== day)) // Remove if already there
    } else{
      setSelectedDays([...selectedDays, day]) //Add if not there
    }
  }
  const handleSubmit = async (e) => {
    e.preventDefault() 
    setLoading(true) // 1. Lock the button
    if (selectedDays.length === 0){
      alert("Please Select at least one day!")
      return
    }

    // Create the object to send to Python
    const newVote = {
      name: name,
      day: selectedDays, 
      note: note
    }

    try {
      // POST the data to your backend
      await axios.post(`${API_BASE_URL}/vote`, newVote)
      
      // Clear the form and refresh the parent list
      setName('')
      setNote('')
      setSelectedDays([])
      onVoteSuccess() 
    } catch (error) {
      if (error.response && error.response.status === 400){
        alert(error.response.data.detail);
        setName('')
      }
    } finally{
      setLoading(false)
    }
  }

  const getWeekDays = (startDay, startMonth, year) =>{
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    const anchor = new Date (year, startMonth - 1, startDay)
    return days.map((dayName, index) => {
      const current = new Date(anchor);
      current.setDate(anchor.getDate() + index);

      const dateString = current.toLocaleDateString('de-DE', {
        day: '2-digit',
        month: '2-digit'
      })
      return{
        name:dayName,
        label: `${dayName} (${dateString})`
      }
    })
  }
  const weekDays = getWeekDays(20, 4, 2026);

return (
    <div style={{ background: '#eee', padding: '20px', borderRadius: '10px' }}>
      <h3>Which day?</h3>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
        <input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} required />
        
        {/* 3. Render Checkboxes for days */}
        <div>
          <p style={{ margin: '0 0 10px 0' }}>Which days are you playing?</p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
            {weekDays.map((day) => (
            <label key={day.name}>
              <input
                type="checkbox"
                checked={selectedDays.includes(day.name)} // Add this to keep the box checked
                onChange={() => handleDayChange(day.name)} // Wrap it in a function!
              />
              {day.label} {/* Shows "Monday (19.04)" to the user */}
            </label>
          ))}
          </div>
        </div>

        <textarea placeholder="Note" value={note} onChange={(e) => setNote(e.target.value)} />
        <button type="submit" disabled={loading} style={{ backgroundColor: '#007bff', color: 'white', padding: '10px' }}>
          {loading ? "Sending..." : "Send Vote 🏓"}
        </button>
      </form>
    </div>
  )
}

export default VoteForm