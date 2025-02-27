import React, { useState, useEffect } from "react";
import axios from "axios";
import { Cropper } from "react-cropper";
import "cropperjs/dist/cropper.css";
import Confetti from "react-confetti";
import "./App.css"; 
import { lightTheme, darkTheme } from "./theme";
const App = () => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [darkMode, setDarkMode] = useState(false);
  const [croppedImage, setCroppedImage] = useState(null);
  const [uploadCount, setUploadCount] = useState(0);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [history, setHistory] = useState([]);
  const [currentTip, setCurrentTip] = useState("");
  const [showHowToUse, setShowHowToUse] = useState(false); 
  const [showCelebration, setShowCelebration] = useState(false); 

  const farmingTips = [
    "Did you know? Rotating crops can help prevent soil-borne diseases.",
    "Tip: Regularly inspect your plants for early signs of disease.",
    "Fun Fact: Some plants release chemicals to repel pests naturally!",
  ];

  // Load dark mode preference from localStorage
  useEffect(() => {
    const savedDarkMode = localStorage.getItem("darkMode") === "true";
    setDarkMode(savedDarkMode);
    setCurrentTip(farmingTips[Math.floor(Math.random() * farmingTips.length)]);
  }, []);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.size > 5 * 1024 * 1024) {
        setError("File size exceeds the 5MB limit.");
        return;
      }
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setPrediction(null);
      setError(null);
      setUploadCount((prev) => prev + 1);

      // Simulate upload progress
      let progress = 0;
      const interval = setInterval(() => {
        progress += 10;
        setUploadProgress(progress);
        if (progress >= 100) clearInterval(interval);
      }, 200);
    }
  };

  const handleCrop = (cropper) => {
    if (cropper) {
      setCroppedImage(cropper.getCroppedCanvas().toDataURL());
    }
  };

  const handleSubmit = async () => {
    if (!file) {
      setError("Please select an image first!");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post("http://localhost:5000/predict", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setPrediction(response.data);
      setHistory((prev) => [...prev, response.data]);
      setShowCelebration(true); // Trigger celebration animation
      setTimeout(() => setShowCelebration(false), 5000); // Hide celebration after 5 seconds
    } catch (err) {
      setError("Failed to get prediction. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveImage = () => {
    setFile(null);
    setPreview(null);
    setCroppedImage(null);
    setPrediction(null);
    setError(null);
    setUploadProgress(0);
  };

  const toggleDarkMode = () => {
    const newDarkMode = !darkMode;
    setDarkMode(newDarkMode);
    localStorage.setItem("darkMode", newDarkMode);
  };

  const handleFeedback = (isHelpful) => {
    alert(`Thank you for your feedback! You selected: ${isHelpful ? "Helpful" : "Not Helpful"}`);
  };

  const handleShare = () => {
    const text = `I just detected a crop disease using this app! Disease: ${prediction.predicted_disease}, Confidence: ${(prediction.confidence * 100).toFixed(2)}%.`;
    navigator.clipboard.writeText(text);
    alert("Results copied to clipboard!");
  };

  const handleDownloadReport = () => {
    const text = `Crop Disease Detection Report\n\nDisease: ${prediction.predicted_disease}\nConfidence: ${(prediction.confidence * 100).toFixed(2)}%\nTreatment: ${prediction.treatment}`;
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "crop_disease_report.txt";
    link.click();
  };

  const handleReset = () => {
    setFile(null);
    setPreview(null);
    setPrediction(null);
    setError(null);
    setHistory([]);
    setUploadProgress(0);
    setUploadCount(0); // Reset upload count
  };

  const refreshTip = () => {
    const newTip = farmingTips[Math.floor(Math.random() * farmingTips.length)];
    setCurrentTip(newTip);
  };

  const toggleHowToUse = () => {
    console.log("Toggling How to Use section. Current state:", showHowToUse);
    setShowHowToUse(!showHowToUse);
  };

  // Apply theme variables to the root element
  useEffect(() => {
    const root = document.documentElement;
    const theme = darkMode ? darkTheme : lightTheme;
    root.style.setProperty("--background", theme.background);
    root.style.setProperty("--text", theme.text);
    root.style.setProperty("--cardBackground", theme.cardBackground);
    root.style.setProperty("--buttonBackground", theme.buttonBackground);
    root.style.setProperty("--buttonHover", theme.buttonHover);
  }, [darkMode]);

  return (
    <div className="container">
      <nav className="navbar">
        <button className="toggle-button" onClick={toggleDarkMode} title="Switch to Dark Mode">
          {darkMode ? "🌞" : "🌙"}
        </button>
      </nav>
      <div className="content">
        <h1 className="title">Crop Disease Detection</h1>
        <div className="tip-container">
          <p className="tip-text">{currentTip}</p>
          <button className="refresh-tip-button" onClick={refreshTip}>
            New Tip
          </button>
        </div>
        <button className="need-more-button" onClick={toggleHowToUse}>
          {showHowToUse ? "Hide Instructions" : "Need More?"}
        </button>
        {showHowToUse && (
          <div className="how-to-use-section fade-in">
            <h3>How to Use</h3>
            <div className="step">
              <p>1. Upload an image of a crop leaf.</p>
            </div>
            <div className="step">
              <p>2. Click 'Predict Disease' to analyze the image.</p>
            </div>
            <div className="step">
              <p>3. View the results and suggested treatments.</p>
            </div>
          </div>
        )}
        <div className="upload-container">
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="file-input"
          />
          {file && (
            <div className="progress-bar-container">
              <div className="progress-bar" style={{ width: `${uploadProgress}%` }}></div>
            </div>
          )}
          {preview && (
            <Cropper
              src={preview}
              style={{ height: 300, width: "100%" }}
              aspectRatio={1}
              guides={false}
              crop={handleCrop}
            />
          )}
          {croppedImage && (
            <img
              src={croppedImage}
              alt="Cropped"
              className="cropped-image"
              style={{ marginTop: "20px", maxWidth: "100%" }}
            />
          )}
          <button className="button" onClick={handleSubmit} disabled={loading}>
            {loading ? <div className="spinner" /> : "Predict Disease"}
          </button>
          {file && (
            <button className="remove-button" onClick={handleRemoveImage}>
              Remove Image
            </button>
          )}
        </div>

        {loading && <p className="loading-message">Analyzing your image... Please wait.</p>}

        {prediction && (
          <>
            {showCelebration && <Confetti width={window.innerWidth} height={window.innerHeight} recycle={false} />}
            <div className="result-container fade-in">
              <h2 className="result-title">🎉 Prediction Successful! 🎉</h2>
              <p className="result-text">
                <strong>Disease:</strong> {prediction.predicted_disease}
              </p>
              <p className="result-text">
                <strong>Confidence:</strong> {(prediction.confidence * 100).toFixed(2)}%
              </p>
              <p className="result-text">
                <strong>Treatment:</strong> {prediction.treatment}
              </p>
              <div className="feedback-container">
                <p>Was this prediction helpful?</p>
                <button onClick={() => handleFeedback(true)}>Yes</button>
                <button onClick={() => handleFeedback(false)}>No</button>
              </div>
              <button className="share-button" onClick={handleShare}>
                Share Results
              </button>
              <button className="download-button" onClick={handleDownloadReport}>
                Download Report
              </button>
            </div>
          </>
        )}

        {error && <p className="error-text">{error}</p>}

        <div className="history-container">
          <h3>Prediction History</h3>
          {history.map((item, index) => (
            <div key={index} className="history-item">
              <p><strong>Disease:</strong> {item.predicted_disease}</p>
              <p><strong>Confidence:</strong> {(item.confidence * 100).toFixed(2)}%</p>
            </div>
          ))}
        </div>

        <div className="learn-more">
          <h3>Learn More</h3>
          <a href="https://eos.com/blog/crop-diseases/" target="_blank" rel="noopener noreferrer">
            Read about common crop diseases
          </a>
        </div>

        <div className="upload-count">
          <p>You've analyzed <strong>{uploadCount}</strong> images so far. Keep it up!</p>
        </div>

        <button className="reset-button" onClick={handleReset}>
          Reset All
        </button>
      </div>
    </div>
  );
};

export default App;