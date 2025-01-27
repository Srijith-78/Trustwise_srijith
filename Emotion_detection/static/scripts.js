let toxicityChart = null;
let emotionChart = null;

function renderBarChart(canvasId, chartData, chartLabels) {
  const ctx = document.getElementById(canvasId).getContext('2d');

  if (canvasId === 'toxicity-chart' && toxicityChart) {
    toxicityChart.destroy();
  } else if (canvasId === 'emotion-chart' && emotionChart) {
    emotionChart.destroy();
  }

  const newChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: chartLabels,
      datasets: [{
        label: 'Scores',
        data: chartData,
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          max: 1.0
        }
      }
    }
  });

  if (canvasId === 'toxicity-chart') {
    toxicityChart = newChart;
  } else if (canvasId === 'emotion-chart') {
    emotionChart = newChart;
  }
}

function fetchLogs() {
  fetch('http://localhost:8000/logs')
    .then(response => response.json())
    .then(data => {
      if (!Array.isArray(data)) {
        alert('Unexpected data format received.');
        console.error('Expected an array but got:', data);
        return;
      }
      
      const historyTableBody = document.getElementById('history-table-body');
      historyTableBody.innerHTML = '';
      
      data.forEach(log => {
        if (typeof log === 'object' && log !== null) {
          const row = historyTableBody.insertRow();
          
          const textCell = row.insertCell(0);
          const toxicityLabelCell = row.insertCell(1);
          const toxicityScoreCell = row.insertCell(2);
          const emotionLabelCell = row.insertCell(3);
          const emotionScoreCell = row.insertCell(4);
          
          textCell.innerText = log.text || 'N/A';
          toxicityLabelCell.innerText = log.toxicity_label || 'N/A';
          toxicityScoreCell.innerText = log.toxicity_score?.toFixed(2) || 'N/A';
          emotionLabelCell.innerText = log.emotion_label || 'N/A';
          emotionScoreCell.innerText = log.emotion_score?.toFixed(2) || 'N/A';
        } else {
          console.warn('Skipping invalid log entry:', log);
        }
      });
    })
    .catch(error => {
      console.error('Error fetching logs:', error);
      alert('Failed to fetch logs. Please try again later.');
    });
}

function analyzeText() {
  const textInput = document.getElementById("text-input").value.trim();
  
  if (!textInput) {
    alert("Please enter some text for analysis.");
    return;
  }

  const requestData = { text: textInput };
  
  fetch('http://localhost:8000/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestData),
  })
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        alert(data.error);
        return;
      }
      
      document.getElementById("toxicity-result").innerText = `Label: ${data.toxicity.label}`;
      document.getElementById("toxicity-highest-score").innerText = `Score: ${data.toxicity.score.toFixed(2)}`;
      document.getElementById("emotion-result").innerText = `Label: ${data.emotion.label}`;
      document.getElementById("emotion-highest-score").innerText = `Score: ${data.emotion.score.toFixed(2)}`;
      renderBarChart("toxicity-chart", data.toxicity_scores, data.toxicity_labels);
      renderBarChart("emotion-chart", data.emotion_scores, data.emotion_labels);
      updateHistoryTable(data.logs[data.logs.length - 1]);
      document.getElementById('text-input').value = '';
    })
    .catch(error => {
      console.error('Error:', error);
      alert('Failed to analyze text. Please try again.');
    });
}

function updateHistoryTable(log) {
  const tableBody = document.getElementById('history-table-body');
  const row = tableBody.insertRow(0);
  
  row.insertCell(0).textContent = log.text;
  row.insertCell(1).textContent = log.emotion_label;
  row.insertCell(2).textContent = log.emotion_score.toFixed(2);
  row.insertCell(3).textContent = log.toxicity_label;
  row.insertCell(4).textContent = log.toxicity_score.toFixed(2);
}

document.addEventListener('DOMContentLoaded', () => {
  fetchLogs();

  document.getElementById('historyButton').addEventListener('click', () => {
    document.getElementById('historyTable').style.display = 'block';
    document.getElementById('historyButton').style.display = 'none';
  });

  document.getElementById('backButton').addEventListener('click', () => {
    document.getElementById('historyTable').style.display = 'none';
    document.getElementById('historyButton').style.display = 'block';
  });
});