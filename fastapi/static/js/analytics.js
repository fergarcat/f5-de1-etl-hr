// analytics.js - Advanced analytics and reporting for DataTech Solutions

let analyticsData = {};
let charts = {};
let selectedTimeRange = '30d';

// Inicialización cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    console.log('📊 Inicializando DataTech Solutions Analytics...');
    
    initializeAnalyticsPage();
});

function initializeAnalyticsPage() {
    // Cargar datos de analytics
    loadAnalyticsData();
    
    // Configurar controles de tiempo
    setupTimeRangeControls();
    
    // Configurar event listeners
    setupEventListeners();
    
    // Configurar auto-refresh cada 60 segundos
    setInterval(loadAnalyticsData, 60000);
}

function setupEventListeners() {
    // Time range selector
    const timeRangeSelect = document.getElementById('time-range-select');
    if (timeRangeSelect) {
        timeRangeSelect.addEventListener('change', function(e) {
            selectedTimeRange = e.target.value;
            loadAnalyticsData();
        });
    }
    
    // Export button
    document.getElementById('export-analytics-btn')?.addEventListener('click', exportAnalyticsData);
    
    // Refresh button
    document.getElementById('refresh-analytics-btn')?.addEventListener('click', refreshAnalytics);
}

/**
 * Cargar datos de analytics
 */
async function loadAnalyticsData() {
    try {
        console.log('📈 Cargando datos de analytics de DataTech Solutions...');
        showLoading();
        
        const [analyticsResponse, kpiResponse, etlMetricsResponse] = await Promise.all([
            fetch(`/api/analytics/summary?period=${selectedTimeRange}`),
            fetch(`/api/analytics/kpis?period=${selectedTimeRange}`),
            fetch(`/api/analytics/etl-metrics?period=${selectedTimeRange}`)
        ]);
        
        if (analyticsResponse.ok) {
            const data = await analyticsResponse.json();
            if (data.status === 'success') {
                analyticsData = data.analytics;
                renderAllCharts();
            }
        }
        
        if (kpiResponse.ok) {
            const kpiData = await kpiResponse.json();
            if (kpiData.status === 'success') {
                updateKPICards(kpiData.kpis);
            }
        }

        if (etlMetricsResponse.ok) {
            const etlData = await etlMetricsResponse.json();
            if (etlData.status === 'success') {
                updateETLMetrics(etlData.metrics);
            }
        }
        
        hideLoading();
        
    } catch (error) {
        console.error('❌ Error cargando analytics:', error);
        showErrorMessage('Error cargando datos de analytics');
        hideLoading();
    }
}

/**
 * Update KPI cards with real data
 */
function updateKPICards(kpis) {
    const defaults = {
        total_records: 0,
        processing_rate: 0,
        data_quality: 0,
        active_pipelines: 0
    };
    
    const data = { ...defaults, ...kpis };
    
    // Update KPI values
    document.getElementById('total-records').textContent = data.total_records.toLocaleString();
    document.getElementById('processing-rate').textContent = data.processing_rate.toFixed(2) + '/min';
    document.getElementById('data-quality').textContent = data.data_quality.toFixed(1) + '%';
    document.getElementById('active-pipelines').textContent = data.active_pipelines;
    
    // Add trend indicators
    updateTrendIndicators(data.trends || {});
}

function updateTrendIndicators(trends) {
    const indicators = {
        'records-trend': trends.records || 0,
        'rate-trend': trends.processing_rate || 0,
        'quality-trend': trends.data_quality || 0,
        'pipelines-trend': trends.active_pipelines || 0
    };
    
    Object.entries(indicators).forEach(([id, trend]) => {
        const element = document.getElementById(id);
        if (element) {
            const isPositive = trend > 0;
            const icon = isPositive ? 'fa-arrow-up' : 'fa-arrow-down';
            const colorClass = isPositive ? 'text-success' : 'text-danger';
            
            element.innerHTML = `<i class="fas ${icon} ${colorClass}"></i> ${Math.abs(trend).toFixed(1)}%`;
        }
    });
}

/**
 * Update ETL metrics section
 */
function updateETLMetrics(metrics) {
    // Data type distribution
    updateDataTypeChart(metrics.data_types || []);
    
    // Processing timeline
    updateProcessingTimeline(metrics.processing_timeline || []);
    
    // Error analysis
    updateErrorAnalysis(metrics.errors || []);
    
    // Performance metrics
    updatePerformanceMetrics(metrics.performance || {});
}

/**
 * Renderizar todos los gráficos
 */
function renderAllCharts() {
    if (!analyticsData) return;
    
    renderEmployeeDistribution();
    renderDepartmentAnalysis();
    renderSalaryAnalysis();
    renderGeographicDistribution();
    renderTimelineChart();
    updateDataQuality();
}

/**
 * Employee distribution chart
 */
function renderEmployeeDistribution() {
    const ctx = document.getElementById('employee-distribution-chart');
    if (!ctx || !analyticsData.employee_distribution) return;
    
    // Destroy existing chart
    if (charts.employeeDistribution) {
        charts.employeeDistribution.destroy();
    }
    
    const data = {
        labels: analyticsData.employee_distribution.map(item => item.category),
        datasets: [{
            data: analyticsData.employee_distribution.map(item => item.count),
            backgroundColor: [
                '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
            ],
            borderWidth: 2,
            borderColor: '#fff'
        }]
    };
    
    charts.employeeDistribution = new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed * 100) / total).toFixed(1);
                            return `${context.label}: ${context.parsed} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Department analysis chart
 */
function renderDepartmentAnalysis() {
    const ctx = document.getElementById('department-analysis-chart');
    if (!ctx || !analyticsData.departments) return;
    
    if (charts.departmentAnalysis) {
        charts.departmentAnalysis.destroy();
    }
    
    const departmentData = analyticsData.departments.slice(0, 8); // Top 8 departments
    
    const data = {
        labels: departmentData.map(item => item.department),
        datasets: [{
            label: 'Empleados',
            data: departmentData.map(item => item.count),
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 2,
            borderRadius: 6,
            borderSkipped: false,
        }]
    };
    
    charts.departmentAnalysis = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        }
    });
}

/**
 * Salary analysis chart
 */
function renderSalaryAnalysis() {
    const ctx = document.getElementById('salary-analysis-chart');
    if (!ctx || !analyticsData.salary_ranges) return;
    
    if (charts.salaryAnalysis) {
        charts.salaryAnalysis.destroy();
    }
    
    const data = {
        labels: analyticsData.salary_ranges.map(item => item.range),
        datasets: [{
            label: 'Número de Empleados',
            data: analyticsData.salary_ranges.map(item => item.count),
            backgroundColor: 'rgba(75, 192, 192, 0.6)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 2,
            borderRadius: 6,
        }]
    };
    
    charts.salaryAnalysis = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Empleados: ${context.parsed.y}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

/**
 * Geographic distribution chart
 */
function renderGeographicDistribution() {
    const container = document.getElementById('geographic-distribution');
    if (!container || !analyticsData.locations) return;
    
    const locations = analyticsData.locations.slice(0, 10); // Top 10 locations
    
    if (locations.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">No hay datos geográficos disponibles</p>';
        return;
    }
    
    const maxCount = Math.max(...locations.map(l => l.count));
    
    container.innerHTML = locations.map((location, index) => {
        const percentage = (location.count / maxCount) * 100;
        
        return `
            <div class="location-item">
                <div class="location-header">
                    <span class="location-name">${location.city}, ${location.country}</span>
                    <span class="location-count">${location.count}</span>
                </div>
                <div class="location-bar">
                    <div class="location-fill" style="width: ${percentage}%"></div>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Data type distribution chart
 */
function updateDataTypeChart(dataTypes) {
    const ctx = document.getElementById('data-type-chart');
    if (!ctx || !dataTypes.length) return;
    
    if (charts.dataType) {
        charts.dataType.destroy();
    }
    
    const data = {
        labels: dataTypes.map(item => item.type),
        datasets: [{
            data: dataTypes.map(item => item.count),
            backgroundColor: [
                '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'
            ],
            borderWidth: 2,
            borderColor: '#fff'
        }]
    };
    
    charts.dataType = new Chart(ctx, {
        type: 'doughnut',
        data: data,
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

/**
 * Processing timeline chart
 */
function updateProcessingTimeline(timeline) {
    const ctx = document.getElementById('processing-timeline-chart');
    if (!ctx || !timeline.length) return;
    
    if (charts.processingTimeline) {
        charts.processingTimeline.destroy();
    }
    
    const data = {
        labels: timeline.map(item => {
            const date = new Date(item.timestamp);
            return date.toLocaleDateString('es-ES', { 
                month: 'short', 
                day: 'numeric',
                hour: '2-digit'
            });
        }),
        datasets: [{
            label: 'Registros Procesados',
            data: timeline.map(item => item.records_processed),
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderWidth: 3,
            fill: true,
            tension: 0.4
        }]
    };
    
    charts.processingTimeline = new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

/**
 * Timeline chart for overall analytics
 */
function renderTimelineChart() {
    const ctx = document.getElementById('timeline-chart');
    if (!ctx || !analyticsData.daily_activity) return;
    
    if (charts.timeline) {
        charts.timeline.destroy();
    }
    
    const timelineData = analyticsData.daily_activity;
    
    const data = {
        labels: timelineData.map(item => {
            const date = new Date(item.date);
            return date.toLocaleDateString('es-ES', { 
                month: 'short', 
                day: 'numeric' 
            });
        }),
        datasets: [{
            label: 'Actividad Diaria',
            data: timelineData.map(item => item.activity),
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: 'rgba(75, 192, 192, 1)',
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointRadius: 6,
            pointHoverRadius: 8
        }]
    };
    
    charts.timeline = new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

/**
 * Error analysis update
 */
function updateErrorAnalysis(errors) {
    const container = document.getElementById('error-analysis');
    if (!container) return;
    
    if (!errors || errors.length === 0) {
        container.innerHTML = `
            <div class="alert alert-success">
                <i class="fas fa-check-circle me-2"></i>
                No se detectaron errores significativos
            </div>
        `;
        return;
    }
    
    container.innerHTML = errors.map(error => `
        <div class="error-item">
            <div class="error-header">
                <span class="error-type">${error.type}</span>
                <span class="badge bg-${getSeverityClass(error.severity)}">${error.count}</span>
            </div>
            <div class="error-description">${error.description}</div>
        </div>
    `).join('');
}

function getSeverityClass(severity) {
    const classes = {
        'low': 'info',
        'medium': 'warning',
        'high': 'danger',
        'critical': 'danger'
    };
    return classes[severity] || 'secondary';
}

/**
 * Performance metrics update
 */
function updatePerformanceMetrics(performance) {
    const metrics = {
        'avg-processing-time': performance.avg_processing_time || 0,
        'throughput': performance.throughput || 0,
        'memory-usage': performance.memory_usage || 0,
        'cpu-usage': performance.cpu_usage || 0
    };
    
    Object.entries(metrics).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            if (id.includes('time')) {
                element.textContent = value.toFixed(2) + 'ms';
            } else if (id.includes('usage')) {
                element.textContent = value.toFixed(1) + '%';
            } else {
                element.textContent = value.toLocaleString();
            }
        }
    });
}

/**
 * Data quality analysis
 */
function updateDataQuality() {
    updateFieldCompleteness();
    updateDataValidation();
}

function updateFieldCompleteness() {
    const container = document.getElementById('field-completeness');
    if (!container) return;
    
    // Data completeness by field type (matching Kafka structure)
    const fields = [
        { name: 'Datos Personales', completeness: 98.5, field: 'personal_data' },
        { name: 'Ubicación', completeness: 94.2, field: 'location' },
        { name: 'Datos Profesionales', completeness: 96.8, field: 'professional_data' },
        { name: 'Datos Bancarios', completeness: 89.3, field: 'bank_data' },
        { name: 'Datos de Red', completeness: 87.1, field: 'net_data' }
    ];
    
    container.innerHTML = fields.map(field => {
        const statusClass = field.completeness >= 95 ? 'success' : 
                           field.completeness >= 85 ? 'warning' : 'danger';
        
        return `
            <div class="quality-item">
                <div class="quality-header">
                    <span class="quality-label">${field.name}</span>
                    <span class="quality-percentage text-${statusClass}">${field.completeness.toFixed(1)}%</span>
                </div>
                <div class="progress" style="height: 6px;">
                    <div class="progress-bar bg-${statusClass}" 
                         style="width: ${field.completeness}%;">
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function updateDataValidation() {
    const container = document.getElementById('data-validation');
    if (!container) return;
    
    // Validation results
    const validations = [
        { rule: 'Formato de email válido', passed: 1847, failed: 3, success_rate: 99.8 },
        { rule: 'Números de teléfono válidos', passed: 1832, failed: 18, success_rate: 99.0 },
        { rule: 'Códigos postales válidos', passed: 1798, failed: 52, success_rate: 97.2 },
        { rule: 'Fechas en formato correcto', passed: 1850, failed: 0, success_rate: 100.0 }
    ];
    
    container.innerHTML = validations.map(validation => {
        const statusClass = validation.success_rate >= 99 ? 'success' : 
                           validation.success_rate >= 95 ? 'warning' : 'danger';
        
        return `
            <div class="validation-item">
                <div class="validation-header">
                    <span class="validation-rule">${validation.rule}</span>
                    <span class="validation-rate text-${statusClass}">${validation.success_rate.toFixed(1)}%</span>
                </div>
                <div class="validation-details">
                    <span class="text-success">✓ ${validation.passed}</span>
                    <span class="text-danger">✗ ${validation.failed}</span>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Time range controls setup
 */
function setupTimeRangeControls() {
    const timeRange = document.getElementById('time-range-select');
    if (timeRange) {
        timeRange.addEventListener('change', function(e) {
            selectedTimeRange = e.target.value;
            console.log(`📅 Cambiando rango de tiempo a ${selectedTimeRange}`);
            loadAnalyticsData();
        });
    }
}

/**
 * Export analytics data
 */
async function exportAnalyticsData() {
    try {
        showLoading('Exportando datos...');
        
        const response = await fetch('/api/analytics/export', {
            method: 'GET',
            headers: {
                'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            }
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `analytics_datatech_${new Date().toISOString().split('T')[0]}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showSuccessMessage('Reporte exportado exitosamente');
        } else {
            throw new Error('Error en la exportación');
        }
        
        hideLoading();
    } catch (error) {
        console.error('Error exporting analytics:', error);
        showErrorMessage('Error exportando reporte de analytics');
        hideLoading();
    }
}

/**
 * Refresh all analytics
 */
function refreshAnalytics() {
    console.log('🔄 Actualizando analytics...');
    showSuccessMessage('Actualizando datos...');
    loadAnalyticsData();
}

// Utility functions
function showLoading(message = 'Cargando...') {
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.textContent = message;
        loadingIndicator.style.display = 'block';
    }
}

function hideLoading() {
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.style.display = 'none';
    }
}

function showSuccessMessage(message) {
    // Implement toast notification
    console.log('Success:', message);
}

function showErrorMessage(message) {
    // Implement toast notification
    console.log('Error:', message);
}

// Add custom CSS for analytics
const analyticsCSS = `
    .location-item {
        padding: 12px;
        margin-bottom: 8px;
        background: #f8f9fa;
        border-radius: 6px;
        border-left: 4px solid #0d6efd;
    }
    
    .location-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    
    .location-name {
        font-weight: 500;
        color: #495057;
    }
    
    .location-count {
        font-weight: bold;
        color: #0d6efd;
    }
    
    .location-bar {
        height: 6px;
        background: #e9ecef;
        border-radius: 3px;
        overflow: hidden;
    }
    
    .location-fill {
        height: 100%;
        background: linear-gradient(90deg, #0d6efd, #6c5ce7);
        border-radius: 3px;
        transition: width 0.5s ease;
    }
    
    .quality-item, .validation-item, .error-item {
        margin-bottom: 15px;
        padding: 12px;
        background: #f8f9fa;
        border-radius: 6px;
        border: 1px solid #e9ecef;
    }
    
    .quality-header, .validation-header, .error-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    
    .validation-details {
        display: flex;
        gap: 15px;
        font-size: 0.9em;
    }
    
    .chart-container {
        position: relative;
        height: 300px;
        width: 100%;
    }
    
    @media (max-width: 768px) {
        .chart-container {
            height: 250px;
        }
    }
`;

// Inject CSS if not already present
if (!document.getElementById('analytics-css')) {
    const style = document.createElement('style');
    style.id = 'analytics-css';
    style.textContent = analyticsCSS;
    document.head.appendChild(style);
}
