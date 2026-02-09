// Initialize Charts
document.addEventListener('DOMContentLoaded', function () {
    // Only run if charts are on the page
    if (document.getElementById('projectProgressChart')) {
        initCharts();
    }
});

function initCharts() {
    // Project Progress Chart
    const progressCtx = document.getElementById('projectProgressChart').getContext('2d');
    new Chart(progressCtx, {
        type: 'line',
        data: {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7'],
            datasets: [{
                label: 'Website Redesign',
                data: [15, 25, 40, 55, 65, 75, 85],
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                fill: true,
                tension: 0.4
            }, {
                label: 'Mobile App',
                data: [5, 10, 20, 30, 35, 40, 45],
                borderColor: '#8b5cf6',
                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                fill: true,
                tension: 0.4
            }, {
                label: 'E-commerce Backend',
                data: [20, 40, 60, 75, 85, 90, 92],
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Progress %'
                    }
                }
            }
        }
    });

    // Productivity Chart
    const productivityCtx = document.getElementById('productivityChart')?.getContext('2d');
    if (productivityCtx) {
        new Chart(productivityCtx, {
            type: 'bar',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Tasks Completed',
                    data: [12, 19, 15, 25, 22, 10, 8],
                    backgroundColor: '#3b82f6',
                    borderRadius: 6
                }, {
                    label: 'Tasks Created',
                    data: [8, 12, 10, 18, 15, 5, 3],
                    backgroundColor: '#8b5cf6',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    }
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

    // Task Distribution Chart
    const taskDistCtx = document.getElementById('taskDistributionChart')?.getContext('2d');
    if (taskDistCtx) {
        new Chart(taskDistCtx, {
            type: 'doughnut',
            data: {
                labels: ['Completed', 'In Progress', 'Pending', 'Overdue'],
                datasets: [{
                    data: [42, 23, 15, 8],
                    backgroundColor: [
                        '#10b981',
                        '#3b82f6',
                        '#f59e0b',
                        '#ef4444'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 19,
                            boxWidth: 15,
                            font: { size: 13 }
                        }
                    }
                },
                layout: {
                    padding: {
                        top: 15,
                        bottom: 25,
                        left: 10,
                        right: 10
                    }
                }
            }
        });
    }
}