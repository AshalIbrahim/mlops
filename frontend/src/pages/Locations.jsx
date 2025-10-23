import React, { useEffect, useState } from 'react'
import List from '@mui/material/List'
import ListItem from '@mui/material/ListItem'
import ListItemButton from '@mui/material/ListItemButton'
import ListItemText from '@mui/material/ListItemText'
import Typography from '@mui/material/Typography'
import Button from '@mui/material/Button'
import Stack from '@mui/material/Stack'
import { useNavigate } from 'react-router-dom'

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

export default function Locations({ onSelectLocation }){
  const [locations, setLocations] = useState([])
  const navigate = useNavigate()

  useEffect(()=>{
    fetchLocations()
  },[])

  async function fetchLocations(){
    try{
      const resp = await fetch(API + '/locations')
      const data = await resp.json()
      setLocations(data.locations || [])
    }catch(err){
      console.error('fetchLocations', err)
    }
  }

  function select(loc){
    if(onSelectLocation) onSelectLocation(loc)
    navigate('/')
  }

  return (
    <div>
      <Typography variant="h5" sx={{ mb: 2 }}>Locations</Typography>
      <List>
        {locations.map((loc)=> (
          <ListItem key={loc} disablePadding>
            <ListItemButton onClick={()=>select(loc)}>
              <ListItemText primary={loc} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Stack direction="row" spacing={2} sx={{ mt: 2 }}>
        <Button variant="outlined" onClick={()=>{ if(onSelectLocation) onSelectLocation(null); navigate('/') }}>Clear Filter</Button>
      </Stack>
    </div>
  )
}
