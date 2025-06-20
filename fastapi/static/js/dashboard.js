/**
 * Dashboard.js - Dashboard principal de DataTech Solutions
 * Sistema ETL para gestión de datos de RRHH
 */

// Variables globales
let dashboardCharts = {};
let dashboardData = {};

// Inicialización del dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DataTech Solutions - Dashboard ETL iniciado');
    
    // Cargar datos del dashboard
    loadDashboardData();
    
    // Auto-refresh cada 30 segundos
    setInterval(loadDashboardData, 30000);
    
    // Inicializar controles del pipeline
    initPipelineControls();
});

/**
 * Cargar datos del dashboard
 */
async function loadDashboardData() {
    try {
        console.log('📊 Cargando datos del dashboard...');
        
        // Usar endpoint mock para desarrollo
        const response = await fetch('/api/mock/stats');
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        if (data.status === 'success') {
            dashboardData = data;
            
            // Actualizar métricas ETL
            updateETLMetrics(data);
            
            // Crear gráficos
            createGeographicChart(data.top_cities);
            createJobsChart(data.top_positions);
            
            // Actualizar pipeline status
            updatePipelineStatus();
            
            console.log('✅ Dashboard actualizado correctamente');
        }
        
    } catch (error) {
        console.error('❌ Error cargando datos del dashboard:', error);
        showToast('Error al cargar datos del dashboard', 'error');
    }
}

/**
 * Actualizar métricas ETL
 */
function updateETLMetrics(data) {
    // Total empleados procesados
    animateCounter('total-employees', data.total_processed_users || 0);
    
    // Empresas registradas (contar empresas únicas de top_companies simuladas)
    const companiesCount = data.top_positions ? data.top_positions.length * 3 : 15;
    animateCounter('companies-count', companiesCount);
    
    // Tipos de datos siempre 5
    document.getElementById('data-types-processed').textContent = '5';
    
    // Última sincronización
    const lastSync = new Date().toLocaleTimeString('es-ES');
    document.getElementById('last-sync').textContent = lastSync;
}

/**
 * Animación de contadores
 */
function animateCounter(elementId, targetValue) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const startValue = 0;
    const duration = 1500;
    const startTime = performance.now();
    
    function updateCounter(currentTime) {
        const elapsedTime = currentTime - startTime;
        const progress = Math.min(elapsedTime / duration, 1);
        
        // Easing function
        const easedProgress = 1 - Math.pow(1 - progress, 3);
        const currentValue = Math.floor(startValue + (targetValue - startValue) * easedProgress);
        
        element.textContent = currentValue.toLocaleString();
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        }
    }
    
    requestAnimationFrame(updateCounter);
}

/**
 * Gráfico de distribución geográfica
 */
function createGeographicChart(citiesData) {
    const ctx = document.getElementById('geographicChart');
    if (!ctx) return;
    
    // Destruir gráfico existente
    if (dashboardCharts.geographic) {
        dashboardCharts.geographic.destroy();
    }
    
    const colors = [
        '#2a3563',
        '#3d4878', 
        '#4a90a4',
        '#5c7cfa',
        '#8b7355'
    ];
    
    dashboardCharts.geographic = new Chart(ctx.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: citiesData.map(item => item.city),
            datasets: [{
                data: citiesData.map(item => item.count),
                backgroundColor: colors,
                borderColor: '#ffffff',
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#2a3563',
                        font: { size: 12, weight: '500' },
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: '#2a3563',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
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
 * Gráfico de puestos de trabajo
 */
function createJobsChart(jobsData) {
    const ctx = document.getElementById('jobsChart');
    if (!ctx) return;
    
    // Destruir gráfico existente
    if (dashboardCharts.jobs) {
        dashboardCharts.jobs.destroy();
    }
    
    // Crear gradiente
    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, '#2a3563');
    gradient.addColorStop(0.6, '#3d4878');
    gradient.addColorStop(1, 'rgba(255, 255, 255, 0.8)');
    
    dashboardCharts.jobs = new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: jobsData.map(item => item.position),
            datasets: [{
                label: 'Empleados',
                data: jobsData.map(item => item.count),
                backgroundColor: gradient,
                borderColor: '#2a3563',
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0,
                        color: '#2a3563'
                    },
                    grid: {
                        color: 'rgba(42, 53, 99, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: '#2a3563',
                        maxRotation: 45,
                        minRotation: 45
                    },
                    grid: { display: false }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#2a3563',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff'
                }
            }
        }
    });
}

/**
 * Actualizar estado del pipeline
 */
function updatePipelineStatus() {
    // Actualizar contador de mensajes Kafka (simulado)
    const kafkaCounter = document.getElementById('kafka-messages');
    if (kafkaCounter) {
        const randomMessages = Math.floor(Math.random() * 50) + 20;
        kafkaCounter.textContent = randomMessages;
    }
    
    // Animar iconos del pipeline
    const stageIcons = document.querySelectorAll('.stage-icon');
    stageIcons.forEach(icon => {
        icon.classList.add('active');
    });
}

/**
 * Controles del pipeline
 */
function initPipelineControls() {
    // Los botones ya tienen onclick en el HTML
    console.log('🔧 Controles del pipeline inicializados');
}

/**
 * Iniciar procesamiento ETL
 */
function startETLProcess() {
    console.log('▶️ Iniciando procesamiento ETL...');
    showToast('Procesamiento ETL iniciado', 'success');
    updatePipelineStatus();
}

/**
 * Pausar procesamiento ETL
 */
function pauseETLProcess() {
    console.log('⏸️ Pausando procesamiento ETL...');
    showToast('Procesamiento ETL pausado', 'warning');
}

// Agregar estilos CSS específicos para el pipeline
const pipelineStyles = `
<style>
.pipeline-stage {
    display: flex;
    align-items: center;
    margin-bottom: 1rem;
    padding: 1.5rem;
    background: rgba(42, 53, 99, 0.05);
    border-radius: 8px;
    border-left: 4px solid #2a3563;
    transition: all 0.3s ease;
}

.pipeline-stage:hover {
    background: rgba(42, 53, 99, 0.08);
    transform: translateX(5px);
}

.stage-icon {
    width: 60px;
    height: 60px;
    background: #e9ecef;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 1.5rem;
    transition: all 0.3s ease;
    font-size: 1.5rem;
    color: #6c757d;
}

.stage-icon.active {
    background: linear-gradient(135deg, #2a3563, #3d4878);
    color: white;
    box-shadow: 0 4px 15px rgba(42, 53, 99, 0.3);
    animation: pulse 2s infinite;
}

.stage-info h6 {
    margin: 0 0 0.5rem 0;
    color: #2a3563;
    font-weight: 600;
    font-size: 1.1rem;
}

.stage-info small {
    font-size: 0.9rem;
    line-height: 1.4;
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

@media (max-width: 768px) {
    .pipeline-stage {
        flex-direction: column;
        text-align: center;
        padding: 1rem;
    }
    
    .stage-icon {
        margin-right: 0;
        margin-bottom: 1rem;
    }
}
</style>
`;

// Inyectar estilos
if (!document.getElementById('dashboard-pipeline-css')) {
    const style = document.createElement('style');
    style.id = 'dashboard-pipeline-css';
    style.innerHTML = pipelineStyles;
    document.head.appendChild(style);
}
