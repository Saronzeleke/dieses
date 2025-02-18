import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [result, setResult] = useState(null);

  const handleUpload = async (event) => {
    const file = event.target.files[0];
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:5000/api/detect-disease', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResult(response.data.disease);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div>
      <h1>Crop Disease Detection</h1>
      <input type="file" accept="image/*" onChange={handleUpload} />
      {result && <p>Detected Disease: {result}</p>}
    </div>
  );
}

export default App;