// Configuración global con nueva paleta de colores
const API_BASE = '/api';

// Paleta de colores personalizada
const CHART_COLORS = {
    primary: '#2a3563',
    primaryLight: '#3d4878',
    primaryDark: '#1f2749',
    white: '#ffffff',
    gradients: {
        primary: ['#2a3563', '#3d4878', '#ffffff'],
        success: ['#2a3563', '#4a90a4', '#ffffff'],
        warning: ['#2a3563', '#8b7355', '#ffffff'],
        info: ['#2a3563', '#5c7cfa', '#ffffff']
    }
};

// Variables globales
let citiesChart, positionsChart;

// Actualizar reloj
function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('es-ES');
    const clockElement = document.getElementById('current-time');
    if (clockElement) {
        clockElement.textContent = timeString;
    }
}

// API calls mejoradas
async function apiCall(endpoint) {
    try {
        showLoadingState(true);
        const response = await fetch(`${API_BASE}${endpoint}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        showLoadingState(false);
        return data;
    } catch (error) {
        console.error(`API call failed for ${endpoint}:`, error);
        showLoadingState(false);
        showToast(`Error: ${error.message}`, 'error');
        
        // Fallback a datos mock si la API real falla
        if (endpoint === '/stats') {
            return await fetch(`${API_BASE}/mock/stats`).then(r => r.json());
        }
        throw error;
    }
}

// Estados de carga
function showLoadingState(isLoading) {
    const spinner = document.querySelector('.custom-spinner');
    if (spinner) {
        spinner.style.display = isLoading ? 'block' : 'none';
    }
}

// Toast notifications mejoradas
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    const toastId = 'toast-' + Date.now();
    
    const toastColors = {
        success: 'bg-success',
        error: 'bg-danger',
        warning: 'bg-warning',
        info: 'bg-info'
    };
    
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast align-items-center text-white ${toastColors[type] || toastColors.info} border-0`;
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-${getIconForType(type)} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast, { delay: 5000 });
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function getIconForType(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-triangle',
        warning: 'exclamation-circle',
        info: 'info-circle'
    };
    return icons[type] || icons.info;
}

// Dashboard functions mejoradas
async function loadDashboardData() {
    try {
        const data = await apiCall('/stats');
        
        // Actualizar stats cards con animación
        animateCounter('total-users', data.total_processed_users || 0);
        animateCounter('cache-users', data.users_in_cache || 0);
        
        // Actualizar tiempo
        const lastUpdate = new Date(data.last_updated);
        document.getElementById('last-update').textContent = lastUpdate.toLocaleTimeString();
        
        // Crear gráficos con nueva paleta
        createCitiesChart(data.top_cities || []);
        createPositionsChart(data.top_positions || []);
        
        // Mostrar actividad reciente
        displayRecentActivity(data.recent_activity || []);
        
        // Actualizar estado API
        updateAPIStatus(true);
        
        showToast('Datos actualizados correctamente', 'success');
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        updateAPIStatus(false);
        showToast('Error al cargar datos del dashboard', 'error');
    }
}

// Animación de contadores
function animateCounter(elementId, targetValue) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const startValue = 0;
    const duration = 1500; // 1.5 segundos
    const startTime = performance.now();
    
    function updateCounter(currentTime) {
        const elapsedTime = currentTime - startTime;
        const progress = Math.min(elapsedTime / duration, 1);
        
        // Función de easing
        const easedProgress = 1 - Math.pow(1 - progress, 3);
        const currentValue = Math.floor(startValue + (targetValue - startValue) * easedProgress);
        
        element.textContent = currentValue.toLocaleString();
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        }
    }
    
    requestAnimationFrame(updateCounter);
}

// Gráfico de ciudades mejorado
function createCitiesChart(citiesData) {
    const ctx = document.getElementById('citiesChart');
    if (!ctx) return;
    
    if (citiesChart) {
        citiesChart.destroy();
    }
    
    // Generar gradientes para cada segmento
    const gradientColors = citiesData.map((_, index) => {
        const canvas = ctx;
        const gradient = canvas.getContext('2d').createLinearGradient(0, 0, 0, 400);
        
        const opacity = 1 - (index * 0.15);
        gradient.addColorStop(0, `${CHART_COLORS.primary}${Math.floor(opacity * 255).toString(16).padStart(2, '0')}`);
        gradient.addColorStop(0.5, `${CHART_COLORS.primaryLight}${Math.floor(opacity * 200).toString(16).padStart(2, '0')}`);
        gradient.addColorStop(1, `${CHART_COLORS.white}${Math.floor(opacity * 100).toString(16).padStart(2, '0')}`);
        
        return gradient;
    });
    
    citiesChart = new Chart(ctx.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: citiesData.map(item => item.city || 'N/A'),
            datasets: [{
                data: citiesData.map(item => item.count),
                backgroundColor: gradientColors.length > 0 ? gradientColors : [
                    CHART_COLORS.primary,
                    CHART_COLORS.primaryLight,
                    '#4a90a4',
                    '#5c7cfa',
                    '#8b7355'
                ],
                borderColor: CHART_COLORS.white,
                borderWidth: 3,
                hoverBorderWidth: 5,
                hoverOffset: 10
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
                        usePointStyle: true,
                        color: CHART_COLORS.primary,
                        font: {
                            size: 12,
                            weight: '500'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: CHART_COLORS.primary,
                    titleColor: CHART_COLORS.white,
                    bodyColor: CHART_COLORS.white,
                    borderColor: CHART_COLORS.white,
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: true
                }
            },
            animation: {
                animateRotate: true,
                duration: 2000
            }
        }
    });
}

// Gráfico de posiciones mejorado
function createPositionsChart(positionsData) {
    const ctx = document.getElementById('positionsChart');
    if (!ctx) return;
    
    if (positionsChart) {
        positionsChart.destroy();
    }
    
    // Crear gradiente para las barras
    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, CHART_COLORS.primary);
    gradient.addColorStop(0.6, CHART_COLORS.primaryLight);
    gradient.addColorStop(1, 'rgba(255, 255, 255, 0.8)');
    
    positionsChart = new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: positionsData.map(item => item.position || 'N/A'),
            datasets: [{
                label: 'Usuarios',
                data: positionsData.map(item => item.count),
                backgroundColor: gradient,
                borderColor: CHART_COLORS.primary,
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false,
                hoverBackgroundColor: CHART_COLORS.primaryLight,
                hoverBorderColor: CHART_COLORS.primary,
                hoverBorderWidth: 3
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
                        color: CHART_COLORS.primary,
                        font: {
                            size: 11
                        }
                    },
                    grid: {
                        color: 'rgba(42, 53, 99, 0.1)',
                        lineWidth: 1
                    }
                },
                x: {
                    ticks: {
                        color: CHART_COLORS.primary,
                        font: {
                            size: 11
                        },
                        maxRotation: 45
                    },
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: CHART_COLORS.primary,
                    titleColor: CHART_COLORS.white,
                    bodyColor: CHART_COLORS.white,
                    borderColor: CHART_COLORS.white,
                    borderWidth: 1,
                    cornerRadius: 8
                }
            },
            animation: {
                duration: 2000,
                easing: 'easeOutQuart'
            }
        }
    });
}

// Mostrar actividad reciente mejorada
function displayRecentActivity(recentActivity) {
    const container = document.getElementById('recent-activity');
    if (!container) return;
    
    if (recentActivity.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                <p class="text-muted">No hay actividad reciente</p>
            </div>
        `;
        return;
    }
    
    const activityHTML = recentActivity.map((activity, index) => `
        <div class="activity-item" style="animation-delay: ${index * 0.1}s">
            <div class="d-flex justify-content-between align-items-center p-3 border-bottom border-light">
                <div class="d-flex align-items-center">
                    <div class="activity-avatar">
                        <i class="fas fa-user"></i>
                    </div>
                    <div class="ms-3">
                        <h6 class="mb-1 text-dark">${activity.name}</h6>
                        <small class="text-muted">ID: ${activity.user_id}</small>
                    </div>
                </div>
                <div class="text-end">
                    <small class="text-muted">
                        <i class="fas fa-clock me-1"></i>
                        ${activity.created_at ? new Date(activity.created_at).toLocaleString('es-ES') : 'N/A'}
                    </small>
                </div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = activityHTML;
}

// Estado de API mejorado
function updateAPIStatus(isOnline) {
    const statusElement = document.getElementById('api-status');
    if (statusElement) {
        const icon = statusElement.querySelector('i');
        const text = statusElement.querySelector('.status-text');
        
        if (isOnline) {
            icon.className = 'fas fa-circle text-success';
            text.textContent = 'Sistema Online';
            statusElement.style.color = '#ffffff';
        } else {
            icon.className = 'fas fa-circle text-danger';
            text.textContent = 'Sistema Offline';
            statusElement.style.color = '#ff6b6b';
        }
    }
}

// Auto-refresh mejorado
function startAutoRefresh() {
    const interval = setInterval(() => {
        if (document.getElementById('citiesChart')) {
            loadDashboardData();
        } else {
            clearInterval(interval);
        }
    }, 30000); // 30 segundos
}

// Smooth scroll para navegación
function initSmoothScroll() {
    document.querySelectorAll('.custom-nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            // Solo para anchors internos
            if (this.getAttribute('href').startsWith('#')) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
}

// Inicialización mejorada
document.addEventListener('DOMContentLoaded', function() {
    // Actualizar reloj
    updateClock();
    setInterval(updateClock, 1000);
    
    // Inicializar smooth scroll
    initSmoothScroll();
    
    // Cargar datos si estamos en dashboard
    if (document.getElementById('citiesChart')) {
        loadDashboardData();
        startAutoRefresh();
    }
    
    // Efectos de hover para cards
    document.querySelectorAll('.stats-card, .chart-card, .activity-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Botones de acción
    document.querySelectorAll('.btn-custom').forEach(btn => {
        btn.addEventListener('click', function(e) {
            // Efecto ripple
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
    
    console.log('🚀 HR ETL Dashboard inicializado con nueva paleta de colores');
    showToast('Dashboard cargado correctamente', 'success');
});

// Estilos adicionales para actividad
const additionalStyles = `
    <style>
        .activity-item {
            animation: fadeInLeft 0.6s ease-out both;
        }
        
        .activity-avatar {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #2a3563, #3d4878);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.9rem;
        }
        
        .ripple {
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.6);
            transform: scale(0);
            animation: rippleAnimation 0.6s linear;
            pointer-events: none;
        }
        
        @keyframes fadeInLeft {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes rippleAnimation {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
    </style>
`;

document.head.insertAdjacentHTML('beforeend', additionalStyles);