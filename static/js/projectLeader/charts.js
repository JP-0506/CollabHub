// Global variable to store the chart instance
let projectChart = null;

document.addEventListener('DOMContentLoaded', function () {
    if (document.getElementById('projectProgressChart')) {
        initCharts();
    }
});

function initCharts() {
    const canvas = document.getElementById('projectProgressChart');
    if (!canvas) return;

    // Destroy existing chart if it exists
    if (projectChart) {
        projectChart.destroy();
    }

    // Use data passed from Flask, fallback to empty/defaults
    const labels = window.chartLabels || ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const values = window.chartValues || [0, 0, 0, 0, 0, 0, 0];

    const ctx = canvas.getContext('2d');
    projectChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Tasks Completed',
                data: values,
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Tasks'
                    }
                }
            }
        }
    });
}