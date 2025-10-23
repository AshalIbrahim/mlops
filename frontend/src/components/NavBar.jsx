import React from 'react'
import AppBar from '@mui/material/AppBar'
import Toolbar from '@mui/material/Toolbar'
import Typography from '@mui/material/Typography'
import Button from '@mui/material/Button'
import { Link as RouterLink } from 'react-router-dom'
import Link from '@mui/material/Link'

export default function NavBar(){
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          Zameen
        </Typography>
        <Link component={RouterLink} to="/" color="inherit" underline="none">
          <Button color="inherit">Listings</Button>
        </Link>
        <Link component={RouterLink} to="/locations" color="inherit" underline="none">
          <Button color="inherit">Locations</Button>
        </Link>
        <Link component={RouterLink} to="/predictions" color="inherit" underline="none">
          <Button color="inherit">Predictions</Button>
        </Link>
      </Toolbar>
    </AppBar>
  )
}
