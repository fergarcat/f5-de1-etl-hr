// ========================================
// DASHBOARD.JS - LÓGICA DEL FRONTEND
// ========================================
/**
 * Este archivo maneja toda la lógica del dashboard:
 * 1. Cargar datos desde la API (/api/stats)
 * 2. Crear gráficos con Chart.js
 * 3. Actualizar contadores y métricas
 * 4. Auto-refresh cada 30 segundos
 */

// ========================================
// VARIABLES GLOBALES
// ========================================
let dashboardCharts = {};  
let dashboardData = {};    

// ========================================
// INICIALIZACIÓN - SE EJECUTA AL CARGAR LA PÁGINA
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DataTech Solutions - Dashboard ETL iniciado');
    
    // Cargar datos del dashboard por primera vez
    loadDashboardData();
    
    // Auto-refresh: actualizar datos cada 30 segundos
    setInterval(loadDashboardData, 30000);
    
    console.log('⏰ Auto-refresh configurado cada 30 segundos');
});

// ========================================
// FUNCIÓN PRINCIPAL - CARGAR DATOS
// ========================================
async function loadDashboardData() {
    try {
        console.log('📊 Cargando datos del dashboard...');
        
        // PASO 1: Hacer petición HTTP a la API
        const response = await fetch('/api/stats');
        
        // PASO 2: Verificar que la respuesta sea correcta
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        // PASO 3: Convertir respuesta a JSON
        const data = await response.json();
        console.log('📈 Datos recibidos:', data);
        
        // PASO 4: Guardar datos globalmente
        dashboardData = data;
        
        // PASO 5: Actualizar interfaz con los datos
        updateDashboardMetrics(data);        // Actualizar contadores
        createCitiesChart(data.top_cities);  // Crear gráfico de ciudades
        createDepartmentsChart(data.top_departments); // Crear gráfico de departamentos
        updateLastSync();                    // Actualizar timestamp
        
        console.log('✅ Dashboard actualizado correctamente');
        
    } catch (error) {
        console.error('❌ Error cargando datos del dashboard:', error);
        showErrorMessage('Error al cargar datos del dashboard');
    }
}

// ========================================
// ACTUALIZAR MÉTRICAS Y CONTADORES
// ========================================
function updateDashboardMetrics(data) {
    console.log('📊 Actualizando métricas...');
    
    // Actualizar total de empleados con animación
    animateCounter('total-employees', data.total_employees || 0);
    
    // Actualizar salario promedio
    const avgSalaryElement = document.getElementById('avg-salary');
    if (avgSalaryElement && data.avg_salary) {
        avgSalaryElement.textContent = `${data.avg_salary.toLocaleString('es-ES')} €`;
    }
    
    // Actualizar número de ciudades
    const citiesCountElement = document.getElementById('cities-count');
    if (citiesCountElement && data.top_cities) {
        citiesCountElement.textContent = data.top_cities.length;
    }
    
    // Actualizar número de departamentos
    const departmentsCountElement = document.getElementById('departments-count');
    if (departmentsCountElement && data.top_departments) {
        departmentsCountElement.textContent = data.top_departments.length;
    }
}

// ========================================
// ANIMACIÓN DE CONTADORES
// ========================================
function animateCounter(elementId, targetValue) {
    const element = document.getElementById(elementId);
    if (!element) {
        console.warn(`⚠️ Elemento ${elementId} no encontrado`);
        return;
    }
    
    const startValue = 0;
    const duration = 1500; // 1.5 segundos
    const startTime = performance.now();
    
    function updateCounter(currentTime) {
        const elapsedTime = currentTime - startTime;
        const progress = Math.min(elapsedTime / duration, 1);
        
        // Función de easing para animación suave
        const easedProgress = 1 - Math.pow(1 - progress, 3);
        const currentValue = Math.floor(startValue + (targetValue - startValue) * easedProgress);
        
        // Actualizar el texto del elemento con formato de miles
        element.textContent = currentValue.toLocaleString('es-ES');
        
        // Continuar animación si no ha terminado
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        }
    }
    
    requestAnimationFrame(updateCounter);
}

// ========================================
// GRÁFICO DE DISTRIBUCIÓN POR CIUDADES
// ========================================
function createCitiesChart(citiesData) {
    const canvas = document.getElementById('citiesChart');
    if (!canvas) {
        console.warn('⚠️ Canvas citiesChart no encontrado');
        return;
    }
    
    console.log('🏙️ Creando gráfico de ciudades...');
    
    // Destruir gráfico anterior si existe
    if (dashboardCharts.cities) {
        dashboardCharts.cities.destroy();
    }
    
    // Colores para el gráfico
    const colors = [
        '#2a3563', // Azul oscuro
        '#3d4878', // Azul medio
        '#4a90a4', // Azul claro
        '#5c7cfa', // Azul violeta
        '#8b7355'  // Marrón
    ];
    
    // Crear gráfico de donut
    dashboardCharts.cities = new Chart(canvas.getContext('2d'), {
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
                            return `${context.label}: ${context.parsed} empleados (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
    
    console.log('✅ Gráfico de ciudades creado');
}

// ========================================
// GRÁFICO DE DISTRIBUCIÓN POR DEPARTAMENTOS
// ========================================
function createDepartmentsChart(departmentsData) {
    const canvas = document.getElementById('departmentsChart');
    if (!canvas) {
        console.warn('⚠️ Canvas departmentsChart no encontrado');
        return;
    }
    
    console.log('🏢 Creando gráfico de departamentos...');
    
    // Destruir gráfico anterior si existe
    if (dashboardCharts.departments) {
        dashboardCharts.departments.destroy();
    }
    
    // Crear gradiente para las barras
    const ctx = canvas.getContext('2d');
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, '#2a3563');
    gradient.addColorStop(0.6, '#3d4878');
    gradient.addColorStop(1, 'rgba(255, 255, 255, 0.8)');
    
    // Crear gráfico de barras
    dashboardCharts.departments = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: departmentsData.map(item => item.department),
            datasets: [{
                label: 'Empleados',
                data: departmentsData.map(item => item.count),
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
                    bodyColor: '#ffffff',
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${context.parsed.y} empleados`;
                        }
                    }
                }
            }
        }
    });
    
    console.log('✅ Gráfico de departamentos creado');
}

// ========================================
// FUNCIONES AUXILIARES
// ========================================

function updateLastSync() {
    /**
     * Actualizar timestamp de última sincronización
     */
    const lastSyncElement = document.getElementById('last-sync');
    if (lastSyncElement) {
        const now = new Date();
        lastSyncElement.textContent = now.toLocaleTimeString('es-ES');
    }
}

function showErrorMessage(message) {
    /**
     * Mostrar mensaje de error al usuario
     */
    console.error('💥 Error:', message);
    
    // Crear notificación de error (si existe el elemento)
    const errorElement = document.getElementById('error-message');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
        
        // Ocultar después de 5 segundos
        setTimeout(() => {
            errorElement.style.display = 'none';
        }, 5000);
    }
}

// ========================================
// FUNCIONES PARA ANALYTICS (PÁGINA SEPARADA)
// ========================================

function loadAnalyticsData() {
    /**
     * Cargar datos para la página de analytics
     * Esta función se puede llamar desde analytics.html
     */
    console.log('📈 Cargando datos de analytics...');
    
    // Cargar datos de sueldos por ubicación
    loadSalaryByLocation();
    
    // Cargar datos de sueldos por género
    loadSalaryByGender();
    
    // Cargar datos de sueldos por departamento
    loadSalaryByDepartment();
}

async function loadSalaryByLocation() {
    try {
        const response = await fetch('/api/analytics/salary-by-location');
        const data = await response.json();
        
        // Crear gráfico de sueldos por ubicación
        createSalaryLocationChart(data.salary_by_location);
        
    } catch (error) {
        console.error('Error cargando sueldos por ubicación:', error);
    }
}

async function loadSalaryByGender() {
    try {
        const response = await fetch('/api/analytics/salary-by-gender');
        const data = await response.json();
        
        // Crear gráfico de sueldos por género
        createSalaryGenderChart(data.salary_by_gender);
        
    } catch (error) {
        console.error('Error cargando sueldos por género:', error);
    }
}

async function loadSalaryByDepartment() {
    try {
        const response = await fetch('/api/analytics/salary-by-department');
        const data = await response.json();
        
        // Crear gráfico de sueldos por departamento
        createSalaryDepartmentChart(data.salary_by_department);
        
    } catch (error) {
        console.error('Error cargando sueldos por departamento:', error);
    }
}

function createSalaryLocationChart(data) {
    // TODO: Implementar gráfico de sueldos por ubicación
    console.log('🗺️ Datos de sueldos por ubicación:', data);
}

function createSalaryGenderChart(data) {
    // TODO: Implementar gráfico de sueldos por género
    console.log('👥 Datos de sueldos por género:', data);
}

function createSalaryDepartmentChart(data) {
    // TODO: Implementar gráfico de sueldos por departamento
    console.log('🏢 Datos de sueldos por departamento:', data);
}

// ========================================
// EXPOSICIÓN GLOBAL DE FUNCIONES
// ========================================
// Hacer funciones disponibles globalmente para uso en HTML
window.loadAnalyticsData = loadAnalyticsData;
window.dashboardCharts = dashboardCharts;
window.dashboardData = dashboardData;
