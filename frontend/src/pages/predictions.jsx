import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Predictions = () => {
    const [formData, setFormData] = useState({
        beds: '',
        bathrooms: '',
        coveredArea: '',
        location: '',
        propType: ''
    });
    const [locations, setLocations] = useState([]);
    const [propertyTypes, setPropertyTypes] = useState([]);
    const [predictedPrice, setPredictedPrice] = useState(null);

    useEffect(() => {
        const fetchLocations = async () => {
            try {
                const response = await axios.get('http://localhost:8000/locations');
                setLocations(response.data.locations);
            } catch (error) {
                console.error('Error fetching locations:', error);
            }
        };
        fetchLocations();
        const fetchPropertyTypes = async () => {
            try {
                const resp = await axios.get('http://localhost:8000/prop_type');
                setPropertyTypes(resp.data.prop_type || []);
            } catch (err) {
                console.error('Error fetching property types:', err);
            }
        };
        fetchPropertyTypes();
    }, []);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            // Convert string values to numbers for numeric fields
            const requestData = {
                ...formData,
                beds: parseInt(formData.beds),
                bathrooms: parseInt(formData.bathrooms),
                coveredArea: parseFloat(formData.coveredArea)
            };

            const response = await axios.post('http://localhost:8000/predict', requestData);
            console.log('Response:', response.data); // For debugging
            if (response.data.error) {
                alert('Error: ' + response.data.error);
            } else {
                setPredictedPrice(response.data.formatted_price);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error getting prediction: ' + (error.response?.data?.detail || error.message));
        }
    };

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4">House Price Prediction</h1>
            <form onSubmit={handleSubmit} className="max-w-md">
                <div className="mb-4">
                    <label className="block mb-2">Number of Beds:</label>
                    <input
                        type="number"
                        name="beds"
                        value={formData.beds}
                        onChange={handleChange}
                        className="w-full p-2 border rounded"
                        required
                    />
                </div>
                <div className="mb-4">
                    <label className="block mb-2">Number of Bathrooms:</label>
                    <input
                        type="number"
                        name="bathrooms"
                        value={formData.bathrooms}
                        onChange={handleChange}
                        className="w-full p-2 border rounded"
                        required
                    />
                </div>
                <div className="mb-4">
                    <label className="block mb-2">Covered Area (sq ft):</label>
                    <input
                        type="number"
                        name="coveredArea"
                        value={formData.coveredArea}
                        onChange={handleChange}
                        className="w-full p-2 border rounded"
                        required
                    />
                </div>
                <div className="mb-4">
                    <label className="block mb-2">Location:</label>
                    <select
                        name="location"
                        value={formData.location}
                        onChange={handleChange}
                        className="w-full p-2 border rounded"
                        required
                    >
                        <option value="">Select a location</option>
                        {locations.map((location, index) => (
                            <option key={index} value={location}>
                                {location}
                            </option>
                        ))}
                    </select>
                </div>
                <div className="mb-4">
                    <label className="block mb-2">Property Type:</label>
                    <select
                        name="propType"
                        value={formData.propType}
                        onChange={handleChange}
                        className="w-full p-2 border rounded"
                        required
                    >
                        <option value="">Select a property type</option>
                        {propertyTypes.map((pt, idx) => (
                            <option key={idx} value={pt}>{pt}</option>
                        ))}
                    </select>
                </div>
                <button
                    type="submit"
                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                >
                    Get Prediction
                </button>
            </form>
            {predictedPrice && (
                <div className="mt-4 p-6 bg-white rounded-lg shadow-md">
                    <h2 className="text-xl font-bold mb-2">Predicted Price:</h2>
                    <p className="text-3xl text-green-600 font-bold">{predictedPrice}</p>
                    <p className="text-sm text-gray-500 mt-2">This is an estimated price based on the provided features</p>
                </div>
            )}
        </div>
    );
};

export default Predictions;
