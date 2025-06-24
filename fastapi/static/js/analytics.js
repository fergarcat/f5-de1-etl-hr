// ========================================
// ANALYTICS.JS - FUNCIONALIDADES DE ANALYTICS
// ========================================

class AnalyticsApp {
    constructor() {
        this.charts = {};
        this.data = {};
        this.init();
    }

    async init() {
        await this.loadAnalyticsData();
        this.setupAdvancedCharts();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Botón de refresh si existe
        const refreshBtn = document.querySelector('[data-refresh="analytics"]');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadAnalyticsData());
        }

        // Filtros de tiempo
        const timeFilters = document.querySelectorAll('[data-time-filter]');
        timeFilters.forEach(filter => {
            filter.addEventListener('click', (e) => {
                e.preventDefault();
                this.applyTimeFilter(filter.dataset.timeFilter);
            });
        });

        // Auto-refresh cada 10 minutos
        setInterval(() => this.loadAnalyticsData(), 10 * 60 * 1000);
    }

    async loadAnalyticsData() {
        try {
            this.showLoadingState();

            // Cargar datos de las APIs
            const [stats, employees, departments] = await Promise.all([
                window.hrApp.fetchAPI('/stats'),
                window.hrApp.fetchAPI('/employees'),
                window.hrApp.fetchAPI('/departments')
            ]);

            this.data = { stats, employees, departments };

            // Generar datos adicionales para analytics
            this.generateAnalyticsData();

            // Actualizar la UI
            this.updateAnalyticsMetrics();
            this.updateAdvancedCharts();

            this.hideLoadingState();

        } catch (error) {
            console.error('Error loading analytics data:', error);
            this.hideLoadingState();
            window.hrApp.showToast('Error al cargar datos de analytics', 'error');
        }
    }

    generateAnalyticsData() {
        // Generar datos de tendencias históricas
        this.data.monthlyHiring = this.generateMonthlyHiring();
        this.data.salaryDistribution = this.generateSalaryDistribution();
        this.data.retentionData = this.generateRetentionData();
        this.data.performanceMetrics = this.generatePerformanceMetrics();
    }

    generateMonthlyHiring() {
        const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
        return months.map(month => ({
            month,
            hires: Math.floor(Math.random() * 15) + 5,
            departures: Math.floor(Math.random() * 8) + 2
        }));
    }

    generateSalaryDistribution() {
        return [
            { range: '30k-40k', count: 25 },
            { range: '40k-50k', count: 35 },
            { range: '50k-60k', count: 40 },
            { range: '60k-70k', count: 30 },
            { range: '70k-80k', count: 20 },
            { range: '80k+', count: 15 }
        ];
    }

    generateRetentionData() {
        return [
            { department: 'Engineering', retention: 92 },
            { department: 'Sales', retention: 78 },
            { department: 'Marketing', retention: 85 },
            { department: 'HR', retention: 88 },
            { department: 'Finance', retention: 91 },
            { department: 'Operations', retention: 82 }
        ];
    }

    generatePerformanceMetrics() {
        return {
            productivity: 87,
            satisfaction: 82,
            engagement: 79,
            retention: 85
        };
    }

    showLoadingState() {
        document.querySelectorAll('.analytics-card .card-body').forEach(card => {
            if (!card.querySelector('.spinner-border')) {
                card.insertAdjacentHTML('afterbegin', `
                    <div class="loading-overlay position-absolute w-100 h-100 d-flex align-items-center justify-content-center bg-white bg-opacity-75" style="top: 0; left: 0; z-index: 10;">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Cargando...</span>
                        </div>
                    </div>
                `);
            }
        });
    }

    hideLoadingState() {
        document.querySelectorAll('.loading-overlay').forEach(overlay => {
            overlay.remove();
        });
    }

    updateAnalyticsMetrics() {
        const { stats } = this.data;
        if (!stats) return;

        // Actualizar métricas principales
        const metricsElements = {
            'total-employees-analytics': stats.total_employees,
            'avg-salary-analytics': window.HRUtils.formatCurrency(stats.avg_salary),
            'departments-count': Object.keys(stats.departments).length,
            'new-hires-analytics': stats.new_hires_this_month
        };

        Object.entries(metricsElements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });

        // Actualizar métricas de rendimiento
        const performanceMetrics = this.data.performanceMetrics;
        Object.entries(performanceMetrics).forEach(([metric, value]) => {
            const element = document.getElementById(`${metric}-metric`);
            if (element) {
                element.textContent = `${value}%`;
            }
            
            // Actualizar barras de progreso
            const progressBar = document.getElementById(`${metric}-progress`);
            if (progressBar) {
                progressBar.style.width = `${value}%`;
                progressBar.setAttribute('aria-valuenow', value);
            }
        });
    }

    setupAdvancedCharts() {
        this.setupHiringTrendsChart();
        this.setupSalaryDistributionChart();
        this.setupRetentionChart();
        this.setupDepartmentComparisonChart();
    }

    setupHiringTrendsChart() {
        const ctx = document.getElementById('hiringTrendsChart');
        if (!ctx) return;

        this.charts.hiringTrends = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Contrataciones',
                    data: [],
                    borderColor: 'rgba(40, 167, 69, 1)',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }, {
                    label: 'Salidas',
                    data: [],
                    borderColor: 'rgba(220, 53, 69, 1)',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        position: 'top'
                    }
                }
            }
        });
    }

    setupSalaryDistributionChart() {
        const ctx = document.getElementById('salaryDistributionChart');
        if (!ctx) return;

        this.charts.salaryDistribution = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Número de Empleados',
                    data: [],
                    backgroundColor: 'rgba(0, 123, 255, 0.7)',
                    borderColor: 'rgba(0, 123, 255, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    setupRetentionChart() {
        const ctx = document.getElementById('retentionChart');
        if (!ctx) return;

        this.charts.retention = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Retención (%)',
                    data: [],
                    borderColor: 'rgba(255, 193, 7, 1)',
                    backgroundColor: 'rgba(255, 193, 7, 0.3)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(255, 193, 7, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    setupDepartmentComparisonChart() {
        const ctx = document.getElementById('departmentComparisonChart');
        if (!ctx) return;

        this.charts.departmentComparison = new Chart(ctx, {
            type: 'polarArea',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.7)',
                        'rgba(54, 162, 235, 0.7)',
                        'rgba(255, 205, 86, 0.7)',
                        'rgba(75, 192, 192, 0.7)',
                        'rgba(153, 102, 255, 0.7)',
                        'rgba(255, 159, 64, 0.7)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    updateAdvancedCharts() {
        this.updateHiringTrendsChart();
        this.updateSalaryDistributionChart();
        this.updateRetentionChart();
        this.updateDepartmentComparisonChart();
    }

    updateHiringTrendsChart() {
        if (!this.charts.hiringTrends || !this.data.monthlyHiring) return;

        const chart = this.charts.hiringTrends;
        chart.data.labels = this.data.monthlyHiring.map(item => item.month);
        chart.data.datasets[0].data = this.data.monthlyHiring.map(item => item.hires);
        chart.data.datasets[1].data = this.data.monthlyHiring.map(item => item.departures);
        chart.update();
    }

    updateSalaryDistributionChart() {
        if (!this.charts.salaryDistribution || !this.data.salaryDistribution) return;

        const chart = this.charts.salaryDistribution;
        chart.data.labels = this.data.salaryDistribution.map(item => item.range);
        chart.data.datasets[0].data = this.data.salaryDistribution.map(item => item.count);
        chart.update();
    }

    updateRetentionChart() {
        if (!this.charts.retention || !this.data.retentionData) return;

        const chart = this.charts.retention;
        chart.data.labels = this.data.retentionData.map(item => item.department);
        chart.data.datasets[0].data = this.data.retentionData.map(item => item.retention);
        chart.update();
    }

    updateDepartmentComparisonChart() {
        if (!this.charts.departmentComparison || !this.data.departments) return;

        const chart = this.charts.departmentComparison;
        chart.data.labels = this.data.departments.map(dept => dept.name);
        chart.data.datasets[0].data = this.data.departments.map(dept => dept.employee_count);
        chart.update();
    }

    applyTimeFilter(period) {
        // Actualizar filtros activos
        document.querySelectorAll('[data-time-filter]').forEach(filter => {
            filter.classList.remove('active');
        });
        document.querySelector(`[data-time-filter="${period}"]`).classList.add('active');

        // Recargar datos con el nuevo filtro (implementación futura)
        window.hrApp.showToast(`Filtro aplicado: ${period}`, 'info');
    }
}

// Inicializar analytics cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    // Solo inicializar si estamos en la página de analytics
    if (document.querySelector('#hiringTrendsChart') || document.querySelector('.analytics-card')) {
        window.analyticsApp = new AnalyticsApp();
    }
});
