import React, { useState, useEffect } from 'react';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import NoteModal from './components/NoteModal';
import DrawingCanvas from './components/DrawingCanvas';
import './App.css';

function App() {
  // Authentication states
  const [showRegister, setShowRegister] = useState(false);
  const [registerError, setRegisterError] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loginError, setLoginError] = useState('');
  const [token, setToken] = useState(''); // NEW: Store token
  const [title, setTitle] = useState('');

  // Notes states
  const [content, setContent] = useState('');
  const [keywords, setKeywords] = useState('');
  const [notes, setNotes] = useState([]);
  const [selectedNote, setSelectedNote] = useState(null);
  const [noteMode, setNoteMode] = useState('text'); // 'text' or 'drawing'
  const [drawingData, setDrawingData] = useState(null);
  // Search states
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredNotes, setFilteredNotes] = useState([]);

  // Keep filteredNotes in sync with notes and searchTerm
  useEffect(() => {
    if (searchTerm.trim() === '') {
      setFilteredNotes(notes);
    } else {
      searchByKeywords(searchTerm);
    }
  }, [notes, searchTerm]);

  // Fetch all notes with token
  const fetchAllNotes = async () => {
    try {
      const res = await fetch('http://localhost:8000/notes/', {
        headers: { 'Authorization': `Bearer ${token}` } // FIXED: Added token
      });
      if (res.ok) {
        const allNotes = await res.json();
        setNotes(allNotes);
      }
    } catch (error) {
      console.log("Error fetching notes " + error.message);
    }
  };

  // View note content in modal with token
  const viewNoteContent = async (noteId) => {
    try {
      const res = await fetch(`http://localhost:8000/notes/${noteId}`, {
        headers: { 'Authorization': `Bearer ${token}` } // FIXED: Added token
      });
      if (res.ok) {
        const decryptedNote = await res.json();
        setSelectedNote(decryptedNote);
      } else {
        const errorData = await res.json();
        alert("Error viewing note: " + (errorData.detail || "Unknown error"));
      }
    } catch (error) {
      alert("Error viewing note (network or server error) " + error.message);
    }
  };

  // Registration handler
  const handleRegister = async (username, password) => {
    setRegisterError('');
    try {
      const res = await fetch('http://localhost:8000/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      if (res.ok) {
        setShowRegister(false);
        alert('Registration successful! Please log in.');
      } else {
        const errorData = await res.json();
        setRegisterError(errorData.detail || 'Registration failed');
      }
    } catch (error) {
      setRegisterError('Network error. Please try again. ' + error.message);
    }
  };

  // Login handler - FIXED: Now stores token
  // Login handler - FIXED version
  const handleLogin = async (username, password) => {
    setLoginError('');
    try {
      const res = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      if (res.ok) {
        const data = await res.json();
        const accessToken = data.access_token;
        setToken(accessToken); // This triggers the useEffect below
        setIsLoggedIn(true);
      } else {
        setLoginError('Invalid username or password');
      }
    } catch (error) {
      setLoginError('Network error. Please try again. ' + error.message);
    }
  };

  // NEW: Add this useEffect AFTER the handleLogin function
  useEffect(() => {
    if (isLoggedIn && token) {
      fetchAllNotes();
    }
  }, [isLoggedIn, token]);


  // Create note with token
  // const handleSubmit = async (e) => {
  //   e.preventDefault();
  //   try {
  //     const res = await fetch('http://localhost:8000/notes/', {
  //       method: 'POST',
  //       headers: {
  //         'Content-Type': 'application/json',
  //         'Authorization': `Bearer ${token}` // FIXED: Added token
  //       },
  //       body: JSON.stringify({ title, content, keywords })
  //     });
  //     const data = await res.json();
  //     const updatedNotes = [...notes, data];
  //     setTitle('');
  //     setNotes(updatedNotes);
  //     setContent('');
  //     setKeywords('');
  //   } catch (error) {
  //     alert('Error creating note. Please try again. ' + error);
  //   }
  // };


  // Updated   handleSubmit
  const handleSubmit = async (e) => {
    e.preventDefault();

    let contentToSend = content;
    let drawingToSend = null;

    if (noteMode === 'drawing' && drawingData) {
      drawingToSend = drawingData.imageData;
      contentToSend = '[Drawing Note]';
    }

    try {
      const res = await fetch('http://localhost:8000/notes/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          title,
          content: contentToSend,
          keywords,
          drawing: drawingToSend
        })
      });
      const data = await res.json();
      const updatedNotes = [...notes, data];
      setNotes(updatedNotes);
      setTitle('');
      setContent('');
      setKeywords('');
      setDrawingData(null);
    } catch (error) {
      alert('Error creating note. Please try again. ' + error);
    }
  };

  const handleDrawingSave = (drawing) => {
    setDrawingData(drawing);
    alert('Drawing saved! Add a title and keywords, then click "Save Encrypted Note"');
  };

  // Logout handler
  const handleLogout = () => {
    setIsLoggedIn(false);
    setToken(''); // Clear token
    setNotes([]);
  };

  // Search handler
  const handleSearch = (searchValue) => {
    setSearchTerm(searchValue);
  };

  // Search by keywords with token
  const searchByKeywords = async (searchValue) => {
    try {
      const res = await fetch(`http://localhost:8000/notes/search?q=${encodeURIComponent(searchValue)}`, {
        headers: { 'Authorization': `Bearer ${token}` } // FIXED: Added token
      });

      if (res.ok) {
        const searchResults = await res.json();
        setFilteredNotes(searchResults);
      } else {
        setFilteredNotes([]);
      }
    } catch (error) {
      setFilteredNotes([]);
      console.log(error);
    }
  };

  // Main render
  return (
    <div className="app-container">
      {isLoggedIn ? (
        <>
          <div className="app-header">
            <h1 className="app-title">🔒 Encrypted Notes</h1>
            <button className="logout-btn" onClick={handleLogout}>
              Logout
            </button>
          </div>

          {/* <form className="note-form" onSubmit={handleSubmit}>
            <input
              className="form-input"
              value={title}
              onChange={e => setTitle(e.target.value)}
              placeholder="Note title"
              required
            />
            <textarea
              className="form-textarea"
              value={content}
              onChange={e => setContent(e.target.value)}
              placeholder="Write your encrypted note here..."
              required
            />
            <input
              className="form-input"
              value={keywords}
              onChange={e => setKeywords(e.target.value)}
              placeholder="Keywords (comma separated)"
            />
            <button type="submit" className="save-btn">
              💾 Save Encrypted Note
            </button>
          </form> */}
          <div className="note-input-section">
            <div className="mode-toggle">
              <button
                type="button"
                className={`mode-btn ${noteMode === 'text' ? 'active' : ''}`}
                onClick={() => setNoteMode('text')}
              >
                ✍️ Text Note
              </button>
              <button
                type="button"
                className={`mode-btn ${noteMode === 'drawing' ? 'active' : ''}`}
                onClick={() => setNoteMode('drawing')}
              >
                ✏️ Draw Note
              </button>
            </div>

            <form className="note-form" onSubmit={handleSubmit}>
              <input
                className="form-input"
                value={title}
                onChange={e => setTitle(e.target.value)}
                placeholder="Note title"
                required
              />

              {noteMode === 'text' ? (
                <textarea
                  className="form-textarea"
                  value={content}
                  onChange={e => setContent(e.target.value)}
                  placeholder="Write your encrypted note here..."
                  required={noteMode === 'text'}
                />
              ) : (
                <DrawingCanvas onSave={handleDrawingSave} />
              )}

              <input
                className="form-input"
                value={keywords}
                onChange={e => setKeywords(e.target.value)}
                placeholder="Keywords (comma separated)"
              />

              <button type="submit" className="save-btn">
                💾 Save Encrypted Note
              </button>
            </form>
          </div>



          <div className="notes-section">
            <h2 className="notes-title">Your Encrypted Notes</h2>

            <div className="search-container">
              <input
                type="text"
                className="search-input"
                placeholder="🔍 Search notes..."
                value={searchTerm}
                onChange={(e) => handleSearch(e.target.value)}
              />
              {searchTerm && (
                <div className="search-results-info">
                  Showing {filteredNotes.length} of {notes.length} notes
                </div>
              )}
            </div>

            {filteredNotes.length === 0 ? (
              <p className="empty-state">
                {searchTerm ? 'No notes found matching your search.' : 'No notes yet. Create your first encrypted note above!'}
              </p>
            ) : (
              <ul className="notes-list">
                {filteredNotes.map(note => (
                  <li key={note.id} className="note-item">
                    <div className="note-meta">
                      Created: {new Date(note.created_at).toLocaleDateString()}
                    </div>
                    <div className="note-preview">
                      {note.encrypted_title.slice(0, 50)}...  {/* Show encrypted title */}
                    </div>
                    <button
                      className="view-btn"
                      onClick={() => viewNoteContent(note.id)}
                    >
                      🔓 View Content
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {selectedNote && (
            <NoteModal
              note={selectedNote}
              onClose={() => setSelectedNote(null)}
            />
          )}
        </>
      ) : (
        <div className="auth-container">
          {showRegister ? (
            <div>
              <RegisterForm onRegister={handleRegister} error={registerError} />
              <div className="auth-toggle">
                Already have an account?{' '}
                <button
                  className="auth-link"
                  onClick={() => {
                    setShowRegister(false);
                    setRegisterError('');
                  }}
                >
                  Login
                </button>
              </div>
            </div>
          ) : (
            <div>
              <LoginForm onLogin={handleLogin} error={loginError} />
              <div className="auth-toggle">
                Don't have an account?{' '}
                <button
                  className="auth-link"
                  onClick={() => {
                    setShowRegister(true);
                    setLoginError('');
                  }}
                >
                  Register
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
