document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
});

async function fetchDashboardData(period = 'daily') {
    try {
        const expensesResponse = await fetch(`/get_expenses_over_time/${period}/`);
        const expensesData = await expensesResponse.json();

        const categoryResponse = await fetch('/get_expenses_by_category/');
        const categoryData = await categoryResponse.json();

        const balanceResponse = await fetch('/get_financial_balance/');
        const balanceData = await balanceResponse.json();

        return {
            expenses: expensesData.expenses,
            categories: categoryData.expenses_by_category,
            balance: balanceData
        };
    } catch (error) {
        console.error('Erro ao buscar dados:', error);
    }
}

let charts = {};

async function initializeCharts() {
    const data = await fetchDashboardData();

    charts.expenses = new Chart(document.getElementById('expensesChart'), {
        type: 'line',
        data: {
            labels: ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
            datasets: [{
                label: 'Gastos',
                data: data.expenses,
                borderColor: '#10b981',
                tension: 0.4,
                fill: true,
                backgroundColor: 'rgba(16, 185, 129, 0.1)'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            }
        }
    });

    charts.categories = new Chart(document.getElementById('categoryChart'), {
        type: 'doughnut',
        data: {
            labels: Object.keys(data.categories),
            datasets: [{
                data: Object.values(data.categories),
                backgroundColor: [
                    '#10b981',
                    '#3b82f6',
                    '#f59e0b',
                    '#ef4444',
                    '#8b5cf6'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });

    charts.balance = new Chart(document.getElementById('balanceChart'), {
        type: 'bar',
        data: {
            labels: data.balance.labels,
            datasets: [
                {
                    label: 'Receitas',
                    data: data.balance.income,
                    backgroundColor: '#10b981'
                },
                {
                    label: 'Despesas',
                    data: data.balance.expenses,
                    backgroundColor: '#ef4444'
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function updateTimeRange(period) {
    fetchDashboardData(period).then(data => {
        charts.expenses.data.datasets[0].data = data.expenses;
        charts.expenses.update();
    });
}