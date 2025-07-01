class PlanoGastos {
    constructor() {
        this.doughnutChart = null;
        this.progressCharts = [];
    }

    initialize() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeDoughnutChart();
            this.initializeProgressBars();
        });
    }

    initializeDoughnutChart() {
        const doughnutCtx = document.getElementById('doughnutChart').getContext('2d');
        
        // Configuração do gráfico de rosca
        this.doughnutChart = new Chart(doughnutCtx, {
            type: 'doughnut',
            data: {
                labels: window.categoriaData.map(item => item.nome),
                datasets: [{
                    data: window.categoriaData.map(item => item.valor),
                    backgroundColor: window.categoriaData.map(item => item.cor),
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                cutout: '70%'
            }
        });
    }

    initializeProgressBars() {
        window.despesasData.forEach(despesa => {
            const barCtx = document.getElementById(`barChart${despesa.id}`).getContext('2d');
            
            const progressChart = new Chart(barCtx, {
                type: 'bar',
                data: {
                    labels: ['Progresso'],
                    datasets: [{
                        data: [despesa.percentual_gasto],
                        backgroundColor: despesa.cor,
                        barThickness: 10,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            display: false
                        },
                        x: {
                            display: false
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: (context) => {
                                    return `${context.raw}% concluído`;
                                }
                            }
                        }
                    }
                }
            });

            this.progressCharts.push(progressChart);
        });
    }

    // Método para atualizar os dados do gráfico de rosca
    updateDoughnutData(newData) {
        if (this.doughnutChart) {
            this.doughnutChart.data.labels = newData.map(item => item.nome);
            this.doughnutChart.data.datasets[0].data = newData.map(item => item.valor);
            this.doughnutChart.data.datasets[0].backgroundColor = newData.map(item => item.cor);
            this.doughnutChart.update();
        }
    }

    // Método para atualizar as barras de progresso
    updateProgressBars(newData) {
        newData.forEach((despesa, index) => {
            if (this.progressCharts[index]) {
                this.progressCharts[index].data.datasets[0].data = [despesa.percentual_gasto];
                this.progressCharts[index].data.datasets[0].backgroundColor = despesa.cor;
                this.progressCharts[index].update();
            }
        });
    }

    // Método para destruir todos os gráficos (útil ao sair da página)
    destroy() {
        if (this.doughnutChart) {
            this.doughnutChart.destroy();
        }
        
        this.progressCharts.forEach(chart => {
            if (chart) {
                chart.destroy();
            }
        });
        
        this.progressCharts = [];
    }
}

// Exporta a classe para uso global
window.PlanoGastos = PlanoGastos;