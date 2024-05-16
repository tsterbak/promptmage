import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css'; // Make sure this CSS file is in your src folder

function App() {
  const [functions, setFunctions] = useState([]);
  const [inputs, setInputs] = useState({});
  const [results, setResults] = useState({});

  useEffect(() => {
    axios.get('http://localhost:8000/api/steps')
      .then(response => {
        const functionsData = response.data.map(func => ({
          name: func.name,
          path: func.path,
          parameters: (func.path.match(/\{([^}]+)\}/g) || []).map(p => p.slice(1, -1))
        }));
        setFunctions(functionsData);
      })
      .catch(error => console.error('Error fetching functions', error));
  }, []);

  const handleInputChange = (funcName, paramName, value) => {
    setInputs(prev => ({
      ...prev,
      [funcName]: {
        ...prev[funcName],
        [paramName]: value
      }
    }));
  };

  const executeFunction = (func) => {
    let path = func.path;
    func.parameters.forEach(param => {
      path = path.replace(`{${param}}`, inputs[func.name][param]);
    });

    axios.get(`http://localhost:8000${path}`)
      .then(response => {
        setResults(prev => ({ ...prev, [func.name]: JSON.stringify(response.data) }));
      })
      .catch(error => console.error('Error executing function', error));
  };

  return (
    <div className="app">
      <h1>FlowForge Workbench</h1>
      {functions.map(func => (
        <div key={func.name} className="function">
          <h2>{func.name}</h2>
          {func.parameters.map(param => (
            <input
              key={param}
              type="text"
              placeholder={`Enter ${param}`}
              onChange={(e) => handleInputChange(func.name, param, e.target.value)}
              className="input-field"
            />
          ))}
          <button onClick={() => executeFunction(func)} className="execute-button">Run {func.name}</button>
          <div className="output">
            <strong>Output:</strong>
            <span>{results[func.name] ? results[func.name] : 'No result yet'}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

export default App;
