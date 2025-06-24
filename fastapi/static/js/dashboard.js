// ========================================
// DASHBOARD.JS - FUNCIONALIDADES DEL DASHBOARD
// ========================================

class DashboardApp {
    constructor() {
        this.charts = {};
        this.data = {};
        this.init();
    }

    async init() {
        await this.loadDashboardData();
        this.setupCharts();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Botón de refresh si existe
        const refreshBtn = document.querySelector('[data-refresh="dashboard"]');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadDashboardData());
        }

        // Auto-refresh cada 5 minutos
        setInterval(() => this.loadDashboardData(), 5 * 60 * 1000);
    }

    async loadDashboardData() {
        try {
            // Mostrar indicadores de carga
            this.showLoadingState();

            // Cargar datos de las APIs
            const [stats, employees, departments] = await Promise.all([
                window.hrApp.fetchAPI('/stats'),
                window.hrApp.fetchAPI('/employees'),
                window.hrApp.fetchAPI('/departments')
            ]);

            this.data = { stats, employees, departments };

            // Actualizar la UI
            this.updateStatsCards();
            this.updateCharts();
            this.updateTablesAndLists();

            this.hideLoadingState();

        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.hideLoadingState();
            window.hrApp.showToast('Error al cargar datos del dashboard', 'error');
        }
    }

    showLoadingState() {
        // Agregar indicadores de carga a las tarjetas de estadísticas
        document.querySelectorAll('.stat-card .card-body').forEach(card => {
            const originalContent = card.innerHTML;
            card.setAttribute('data-original', originalContent);
            card.innerHTML = `
                <div class="text-center">
                    <div class="spinner-border spinner-border-sm text-primary" role="status">
                        <span class="visually-hidden">Cargando...</span>
                    </div>
                </div>
            `;
        });
    }

    hideLoadingState() {
        // Remover indicadores de carga
        document.querySelectorAll('.stat-card .card-body[data-original]').forEach(card => {
            const originalContent = card.getAttribute('data-original');
            if (originalContent) {
                card.innerHTML = originalContent;
                card.removeAttribute('data-original');
            }
        });
    }

    updateStatsCards() {
        const { stats } = this.data;
        if (!stats) return;

        // Total empleados
        const totalEmpElement = document.getElementById('total-employees');
        if (totalEmpElement) {
            totalEmpElement.textContent = window.HRUtils.formatNumber(stats.total_employees);
        }

        // Promedio de salario
        const avgSalaryElement = document.getElementById('avg-salary');
        if (avgSalaryElement) {
            avgSalaryElement.textContent = window.HRUtils.formatCurrency(stats.avg_salary);
        }

        // Nuevas contrataciones
        const newHiresElement = document.getElementById('new-hires');
        if (newHiresElement) {
            newHiresElement.textContent = window.HRUtils.formatNumber(stats.new_hires_this_month);
        }

        // Departamentos
        const totalDeptElement = document.getElementById('total-departments');
        if (totalDeptElement) {
            totalDeptElement.textContent = window.HRUtils.formatNumber(Object.keys(stats.departments).length);
        }
    }

    setupCharts() {
        this.setupDepartmentChart();
        this.setupSalaryChart();
        this.setupTrendChart();
    }

    setupDepartmentChart() {
        const ctx = document.getElementById('departmentChart');
        if (!ctx) return;

        this.charts.department = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        '#007bff', '#28a745', '#ffc107', '#dc3545', 
                        '#6f42c1', '#fd7e14', '#20c997', '#6c757d'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }

    setupSalaryChart() {
        const ctx = document.getElementById('salaryChart');
        if (!ctx) return;

        this.charts.salary = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Salario Promedio',
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
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return window.HRUtils.formatCurrency(value);
                            }
                        }
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

    setupTrendChart() {
        const ctx = document.getElementById('trendChart');
        if (!ctx) return;

        // Datos de ejemplo para el gráfico de tendencias
        const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'];
        const hiringData = [8, 12, 6, 15, 10, 5];

        this.charts.trend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [{
                    label: 'Contrataciones',
                    data: hiringData,
                    borderColor: 'rgba(40, 167, 69, 1)',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
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
                        display: false
                    }
                }
            }
        });
    }

    updateCharts() {
        const { stats, departments } = this.data;
        if (!stats || !departments) return;

        // Actualizar gráfico de departamentos
        if (this.charts.department) {
            this.charts.department.data.labels = Object.keys(stats.departments);
            this.charts.department.data.datasets[0].data = Object.values(stats.departments);
            this.charts.department.update();
        }

        // Actualizar gráfico de salarios por departamento
        if (this.charts.salary) {
            this.charts.salary.data.labels = departments.map(dept => dept.name);
            this.charts.salary.data.datasets[0].data = departments.map(dept => dept.avg_salary);
            this.charts.salary.update();
        }
    }

    updateTablesAndLists() {
        this.updateRecentEmployees();
        this.updateDepartmentsList();
    }

    updateRecentEmployees() {
        const { employees } = this.data;
        if (!employees) return;

        const tableBody = document.querySelector('#recent-employees-table tbody');
        if (!tableBody) return;

        // Mostrar los primeros 5 empleados
        const recentEmployees = employees.slice(0, 5);
        
        tableBody.innerHTML = recentEmployees.map(emp => `
            <tr>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="avatar-sm bg-primary rounded-circle d-flex align-items-center justify-content-center me-2">
                            <small class="text-white fw-bold">${emp.name.split(' ').map(n => n[0]).join('')}</small>
                        </div>
                        <div>
                            <div class="fw-bold">${emp.name}</div>
                            <small class="text-muted">${emp.department}</small>
                        </div>
                    </div>
                </td>
                <td>${window.HRUtils.formatCurrency(emp.salary)}</td>
                <td>${window.HRUtils.formatDate(emp.hire_date)}</td>
                <td>
                    <span class="badge bg-success">Activo</span>
                </td>
            </tr>
        `).join('');
    }

    updateDepartmentsList() {
        const { departments } = this.data;
        if (!departments) return;

        const listContainer = document.querySelector('#departments-list');
        if (!listContainer) return;

        listContainer.innerHTML = departments.map(dept => `
            <div class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="mb-1">${dept.name}</h6>
                    <small class="text-muted">${dept.employee_count} empleados</small>
                </div>
                <div class="text-end">
                    <div class="fw-bold">${window.HRUtils.formatCurrency(dept.avg_salary)}</div>
                    <small class="text-muted">Promedio</small>
                </div>
            </div>
        `).join('');
    }
}

// Inicializar dashboard cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    // Solo inicializar si estamos en la página del dashboard
    if (document.querySelector('#departmentChart') || document.querySelector('.stat-card')) {
        window.dashboardApp = new DashboardApp();
    }
});
