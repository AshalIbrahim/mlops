import React from 'react'
import AppBar from '@mui/material/AppBar'
import Toolbar from '@mui/material/Toolbar'
import Typography from '@mui/material/Typography'
import Button from '@mui/material/Button'
import { Link as RouterLink } from 'react-router-dom'
import Link from '@mui/material/Link'

export default function NavBar(){
  return (
    <AppBar 
      position="static"
      sx={{
        background: 'linear-gradient(90deg, #6a1b9a, #8e24aa, #ab47bc)',
        boxShadow: '0 4px 20px rgba(106, 27, 154, 0.3)',
      }}
    >
      <Toolbar>
        <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 700 }}>
          Zameen
        </Typography>
        <Link component={RouterLink} to="/" color="inherit" underline="none">
          <Button 
            color="inherit"
            sx={{
              '&:hover': {
                background: 'rgba(255, 255, 255, 0.1)',
              },
            }}
          >
            Listings
          </Button>
        </Link>
        <Link component={RouterLink} to="/locations" color="inherit" underline="none">
          <Button 
            color="inherit"
            sx={{
              '&:hover': {
                background: 'rgba(255, 255, 255, 0.1)',
              },
            }}
          >
            Locations
          </Button>
        </Link>
        <Link component={RouterLink} to="/predictions" color="inherit" underline="none">
          <Button 
            color="inherit"
            sx={{
              '&:hover': {
                background: 'rgba(255, 255, 255, 0.1)',
              },
            }}
          >
            Predictions
          </Button>
        </Link>
        <Link component={RouterLink} to="/chatbot" color="inherit" underline="none">
          <Button 
            color="inherit"
            sx={{
              '&:hover': {
                background: 'rgba(255, 255, 255, 0.1)',
              },
            }}
          >
            Chatbot
          </Button>
        </Link>
      </Toolbar>
    </AppBar>
  )
}
