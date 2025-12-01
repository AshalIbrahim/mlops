import React, { useEffect, useState } from 'react'
import Grid from '@mui/material/Grid'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import CardActions from '@mui/material/CardActions'
import Typography from '@mui/material/Typography'
import Box from '@mui/material/Box'
import Chip from '@mui/material/Chip'
import IconButton from '@mui/material/IconButton'
import FavoriteBorder from '@mui/icons-material/FavoriteBorder'
import Visibility from '@mui/icons-material/Visibility'
import Filters from '../components/Filters'

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

export default function Listings({ filterLocation }){
  const [listings, setListings] = useState([])
  const [allListings, setAllListings] = useState([])
  const [limit, setLimit] = useState(20)
  const [locations, setLocations] = useState([])
  const [selectedLocation, setSelectedLocation] = useState(filterLocation || '')
  const [filters, setFilters] = useState({ type: '', location: '', minPrice: '', maxPrice: '' })

  useEffect(()=>{
    fetchLocations()
  },[])

  useEffect(()=>{
    fetchListings()
  },[limit, selectedLocation])

  useEffect(()=>{
    applyFilters()
  }, [filters, allListings])

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
      setAllListings(filtered)
      setListings(filtered)
    }catch(err){
      console.error('fetchListings', err)
    }
  }

  function applyFilters(){
    let filtered = allListings.slice()
    if(filters.location){
      filtered = filtered.filter(d => d.location === filters.location)
    }
    if(filters.type){
      filtered = filtered.filter(d => (d.prop_type || '').toLowerCase() === filters.type.toLowerCase())
    }
    const minP = Number(filters.minPrice) || null
    const maxP = Number(filters.maxPrice) || null
    if(minP) filtered = filtered.filter(d => Number(d.price) >= minP)
    if(maxP) filtered = filtered.filter(d => Number(d.price) <= maxP)
    setListings(filtered)
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

  function formatPrice(p){
    if(p===undefined || p===null) return 'N/A'
    const num = Number(p)
    if(Number.isNaN(num)) return p
    return num.toLocaleString(undefined, { style: 'currency', currency: 'PKR', maximumFractionDigits:0 })
  }

  return (
    <div>
      <Filters filters={filters} setFilters={setFilters} onApply={applyFilters} />
      <Grid container spacing={3}>
        {listings.map((l, i) => (
          <Grid item xs={12} md={6} lg={4} key={i}>
            <Card className="property-card">
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent:'space-between', alignItems:'center', mb:1 }}>
                  <Typography variant="h6" sx={{ fontWeight:700 }}>{l.prop_type} <Typography component="span" sx={{ ml:1, fontSize:12, color:'gray' }}>{l.purpose}</Typography></Typography>
                  <Chip label={l.location} size="small" />
                </Box>
                <Typography variant="subtitle1" sx={{ color: 'var(--primary)' , fontWeight:700 }}>{formatPrice(l.price)}</Typography>
                <Typography variant="body2" sx={{ mt:1, color:'rgba(0,0,0,0.7)' }}>{l.covered_area || 'Area N/A'}</Typography>
                <Typography variant="body2" sx={{ mt:0.5, color:'rgba(0,0,0,0.7)'}}>Beds: {l.beds || '-'} &nbsp;|&nbsp; Baths: {l.baths || '-'}</Typography>
              </CardContent>
              <CardActions disableSpacing>
                <IconButton aria-label="view"><Visibility /></IconButton>
                <IconButton aria-label="save"><FavoriteBorder /></IconButton>
                <Box sx={{ flexGrow:1 }} />
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </div>
  )
}
