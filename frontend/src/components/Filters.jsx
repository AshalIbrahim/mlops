import React from 'react'
import Box from '@mui/material/Box'
import TextField from '@mui/material/TextField'
import MenuItem from '@mui/material/MenuItem'
import Button from '@mui/material/Button'

const propertyTypes = [
  { value: 'house', label: 'House' },
  { value: 'apartment', label: 'Apartment' },
  { value: 'plot', label: 'Plot' },
]

export default function Filters({ filters, setFilters, onApply }) {
  return (
    <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 2 }}>
      <TextField
        select
        label="Type"
        value={filters.type || ''}
        onChange={e => setFilters(f => ({ ...f, type: e.target.value }))}
        sx={{ minWidth: 120 }}
      >
        {propertyTypes.map(opt => (
          <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
        ))}
      </TextField>
      <TextField
        label="Location"
        value={filters.location || ''}
        onChange={e => setFilters(f => ({ ...f, location: e.target.value }))}
        sx={{ minWidth: 120 }}
      />
      <TextField
        label="Min Price"
        type="number"
        value={filters.minPrice || ''}
        onChange={e => setFilters(f => ({ ...f, minPrice: e.target.value }))}
        sx={{ minWidth: 100 }}
      />
      <TextField
        label="Max Price"
        type="number"
        value={filters.maxPrice || ''}
        onChange={e => setFilters(f => ({ ...f, maxPrice: e.target.value }))}
        sx={{ minWidth: 100 }}
      />
      <Button variant="contained" onClick={onApply}>Apply</Button>
    </Box>
  )
}
