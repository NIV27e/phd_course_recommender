import React, { useEffect, useState } from 'react';

function App() {
  const [courses, setCourses] = useState([]);
  const [courseId, setCourseId] = useState(1); // Default to 1 for testing
  const [error, setError] = useState('');

  const fetchRecommendations = () => {
    fetch(`http://127.0.0.1:8000/api/recommend/${courseId}/`)
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => setCourses(data))
      .catch(error => setError(error.message));
  };

  useEffect(() => {
    fetchRecommendations();
  }, [courseId]);

  const handleCourseIdChange = (event) => {
    setCourseId(event.target.value);
  };

  const handleGetRecommendations = () => {
    fetchRecommendations();
  };

  return (
    <div className="App">
      <h1>Recommended Courses</h1>
      <input 
        type="number" 
        value={courseId} 
        onChange={handleCourseIdChange} 
        placeholder="Enter course ID" 
      />
      <button onClick={handleGetRecommendations}>Get Recommendations</button>
      {error && <p>Error: {error}</p>}
      <ul>
        {courses.map((course, index) => (
          <li key={index}>
            <h2>{course.title}</h2>
            <p>{course.description}</p>
            <p><strong>University:</strong> {course.university}</p>
            <p><strong>Location:</strong> {course.location}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
