import React, { useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import Container from '@mui/material/Container'
import NavBar from './components/NavBar'

import Listings from './pages/Listings'
import Locations from './pages/Locations'
import Predictions from './pages/predictions'
import ChatBotPage from './pages/ChatBotPage'


export default function App(){
  const [filterLocation, setFilterLocation] = useState(null)

  return (
    <div>
      <NavBar />
      <Container sx={{ mt: 4 }}>
        <Routes>
          <Route path="/" element={<Listings filterLocation={filterLocation} />} />
          <Route path="/locations" element={<Locations onSelectLocation={setFilterLocation} />} />
          <Route path="/predictions" element={<Predictions />} />
          <Route path="/chatbot" element={<ChatBotPage />} />
        </Routes>
      </Container>
    </div>
  )
}
