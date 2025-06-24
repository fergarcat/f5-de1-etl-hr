// ========================================
// APP.JS - FUNCIONALIDADES GENERALES
// ========================================

class HRApp {
    constructor() {
        this.apiBaseUrl = window.location.origin + '/api';
        this.init();
    }

    init() {
        this.updateCurrentTime();
        this.checkApiStatus();
        this.setupEventListeners();
        
        // Actualizar el reloj cada segundo
        setInterval(() => this.updateCurrentTime(), 1000);
        
        // Verificar estado de API cada 30 segundos
        setInterval(() => this.checkApiStatus(), 30000);
    }

    setupEventListeners() {
        // Manejar navegación suave
        document.querySelectorAll('a[href^="/"]').forEach(link => {
            link.addEventListener('click', (e) => {
                // Solo para enlaces internos, no para API docs o externos
                if (link.getAttribute('href') === '/docs') {
                    e.preventDefault();
                    window.open('/docs', '_blank');
                }
            });
        });

        // Agregar eventos para botones de refresh si existen
        const refreshButtons = document.querySelectorAll('[data-refresh]');
        refreshButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.refreshData(button.dataset.refresh);
            });
        });
    }

    updateCurrentTime() {
        const timeElement = document.querySelector('.current-time');
        if (timeElement) {
            const now = new Date();
            const timeString = now.toLocaleTimeString('es-ES', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
            timeElement.innerHTML = `<i class="fas fa-clock me-1"></i>${timeString}`;
        }
    }

    async checkApiStatus() {
        const statusElement = document.getElementById('api-status');
        if (!statusElement) return;

        try {
            const response = await fetch(`${this.apiBaseUrl}/stats`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                statusElement.innerHTML = `
                    <i class="fas fa-circle text-success"></i> 
                    <span class="status-text">Sistema Online</span>
                `;
            } else {
                throw new Error('API Error');
            }
        } catch (error) {
            statusElement.innerHTML = `
                <i class="fas fa-circle text-warning"></i> 
                <span class="status-text">Conexión Limitada</span>
            `;
        }
    }

    async refreshData(type) {
        this.showToast('Actualizando datos...', 'info');
        
        try {
            if (type === 'dashboard' && window.dashboardApp) {
                await window.dashboardApp.loadDashboardData();
            } else if (type === 'analytics' && window.analyticsApp) {
                await window.analyticsApp.loadAnalyticsData();
            }
            
            this.showToast('Datos actualizados correctamente', 'success');
        } catch (error) {
            console.error('Error al actualizar datos:', error);
            this.showToast('Error al actualizar datos', 'error');
        }
    }

    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) return;

        const toastId = 'toast-' + Date.now();
        const iconClass = {
            'success': 'fas fa-check-circle text-success',
            'error': 'fas fa-exclamation-circle text-danger',
            'warning': 'fas fa-exclamation-triangle text-warning',
            'info': 'fas fa-info-circle text-info'
        }[type] || 'fas fa-info-circle text-info';

        const toastHTML = `
            <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header">
                    <i class="${iconClass} me-2"></i>
                    <strong class="me-auto">HR Dashboard</strong>
                    <small class="text-muted">ahora</small>
                    <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement);
        toast.show();

        // Limpiar el toast después de que se oculte
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

    async fetchAPI(endpoint) {
        try {
            const response = await fetch(`${this.apiBaseUrl}${endpoint}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`Error fetching ${endpoint}:`, error);
            throw error;
        }
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('es-ES', {
            style: 'currency',
            currency: 'EUR'
        }).format(amount);
    }

    formatNumber(number) {
        return new Intl.NumberFormat('es-ES').format(number);
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }
}

// Utilidades globales
window.HRUtils = {
    formatCurrency: (amount) => new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'EUR'
    }).format(amount),
    
    formatNumber: (number) => new Intl.NumberFormat('es-ES').format(number),
    
    formatDate: (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }
};

// Inicializar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.hrApp = new HRApp();
});
