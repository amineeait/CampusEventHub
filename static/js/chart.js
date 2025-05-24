// Chart.js - Handles the Chart.js integration for analytics

document.addEventListener('DOMContentLoaded', function() {
  // Event Statistics Chart
  if (document.getElementById('eventStatsChart')) {
    initializeEventStatsChart();
  }
  
  // User Events Chart
  if (document.getElementById('userEventsChart')) {
    initializeUserEventsChart();
  }
  
  // Rating Distribution Chart
  if (document.getElementById('ratingDistributionChart')) {
    initializeRatingDistributionChart();
  }
  
  // Attendance Trends Chart
  if (document.getElementById('attendanceTrendsChart')) {
    initializeAttendanceTrendsChart();
  }
});

function initializeEventStatsChart() {
  var ctx = document.getElementById('eventStatsChart').getContext('2d');
  
  // Get data from data attributes
  var chartElement = document.getElementById('eventStatsChart');
  var labels = JSON.parse(chartElement.dataset.labels || '[]');
  var data = JSON.parse(chartElement.dataset.values || '[]');
  
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Event Count',
        data: data,
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            precision: 0
          }
        }
      }
    }
  });
}

function initializeUserEventsChart() {
  var ctx = document.getElementById('userEventsChart').getContext('2d');
  
  // Get data from data attributes
  var chartElement = document.getElementById('userEventsChart');
  var registered = JSON.parse(chartElement.dataset.registered || '[]');
  var attended = JSON.parse(chartElement.dataset.attended || '[]');
  var labels = JSON.parse(chartElement.dataset.labels || '[]');
  
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Registered',
        data: registered,
        borderColor: 'rgba(54, 162, 235, 1)',
        backgroundColor: 'rgba(54, 162, 235, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4
      }, {
        label: 'Attended',
        data: attended,
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            precision: 0
          }
        }
      }
    }
  });
}

function initializeRatingDistributionChart() {
  var ctx = document.getElementById('ratingDistributionChart').getContext('2d');
  
  // Get data from data attributes
  var chartElement = document.getElementById('ratingDistributionChart');
  var ratings = JSON.parse(chartElement.dataset.ratings || '[0,0,0,0,0]');
  
  new Chart(ctx, {
    type: 'pie',
    data: {
      labels: ['1 Star', '2 Stars', '3 Stars', '4 Stars', '5 Stars'],
      datasets: [{
        data: ratings,
        backgroundColor: [
          'rgba(255, 99, 132, 0.7)',
          'rgba(255, 159, 64, 0.7)',
          'rgba(255, 205, 86, 0.7)',
          'rgba(75, 192, 192, 0.7)',
          'rgba(54, 162, 235, 0.7)'
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(255, 159, 64, 1)',
          'rgba(255, 205, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(54, 162, 235, 1)'
        ],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'right'
        }
      }
    }
  });
}

function initializeAttendanceTrendsChart() {
  var ctx = document.getElementById('attendanceTrendsChart').getContext('2d');
  
  // Get data from data attributes
  var chartElement = document.getElementById('attendanceTrendsChart');
  var registrations = JSON.parse(chartElement.dataset.registrations || '[]');
  var attendances = JSON.parse(chartElement.dataset.attendances || '[]');
  var labels = JSON.parse(chartElement.dataset.labels || '[]');
  
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Registrations',
        data: registrations,
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }, {
        label: 'Attendances',
        data: attendances,
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
          ticks: {
            precision: 0
          }
        }
      }
    }
  });
}