import React, { useEffect, useState } from 'react'
import Grid from '@mui/material/Grid'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import Typography from '@mui/material/Typography'
import TextField from '@mui/material/TextField'
import Button from '@mui/material/Button'
import MenuItem from '@mui/material/MenuItem'

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

export default function Listings({ filterLocation }){
  const [listings, setListings] = useState([])
  const [limit, setLimit] = useState(20)
  const [locations, setLocations] = useState([])
  const [selectedLocation, setSelectedLocation] = useState(filterLocation || '')

  useEffect(()=>{
    fetchLocations()
  },[])

  useEffect(()=>{
    fetchListings()
  },[limit, selectedLocation])

  useEffect(()=>{
    if(filterLocation){
      setSelectedLocation(filterLocation)
    }
  },[filterLocation])

  async function fetchListings(){
    try{
      const url = new URL(API + '/listings')
      url.searchParams.set('limit', limit)
      const resp = await fetch(url.toString())
      const data = await resp.json()
      let filtered = data
      if(selectedLocation){
        filtered = data.filter(d => d.location === selectedLocation)
      }
      setListings(filtered)
    }catch(err){
      console.error('fetchListings', err)
    }
  }

  async function fetchLocations(){
    try{
      const resp = await fetch(API + '/locations')
      const data = await resp.json()
      setLocations(data.locations || [])
    }catch(err){
      console.error('fetchLocations', err)
    }
  }

  return (
    <div>
      <Grid container spacing={2} sx={{ mb: 2 }} alignItems="center">
        <Grid item>
          <TextField label="Limit" type="number" value={limit} onChange={e=>setLimit(e.target.value)} />
        </Grid>
        <Grid item>
          <TextField select label="Location" value={selectedLocation} onChange={e=>setSelectedLocation(e.target.value)} sx={{ minWidth: 200 }}>
            <MenuItem value="">All</MenuItem>
            {locations.map(loc => <MenuItem key={loc} value={loc}>{loc}</MenuItem>)}
          </TextField>
        </Grid>
        <Grid item>
          <Button variant="contained" onClick={fetchListings}>Refresh</Button>
        </Grid>
      </Grid>

      <Grid container spacing={2}>
        {listings.map((l, i) => (
          <Grid item xs={12} md={6} lg={4} key={i}>
            <Card>
              <CardContent>
                <Typography variant="subtitle1">{l.prop_type} — {l.purpose}</Typography>
                <Typography variant="body2">Location: {l.location}</Typography>
                <Typography variant="body2">Area: {l.covered_area}</Typography>
                <Typography variant="body2">Price: {l.price}</Typography>
                <Typography variant="body2">Beds: {l.beds} | Baths: {l.baths}</Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </div>
  )
}
