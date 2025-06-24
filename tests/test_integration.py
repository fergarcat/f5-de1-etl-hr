# ========================================
# TEST_INTEGRATION.PY - TESTS DE INTEGRACIÓN
# ========================================

import pytest
import requests
import sys
import os
import time
from datetime import datetime

# Agregar el directorio raíz al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ========================================
# CONFIGURACIÓN
# ========================================

BASE_URL = "http://localhost:8000"
API_TIMEOUT = 10

class TestSystemIntegration:
    """Tests de integración del sistema completo"""
    
    @classmethod
    def setup_class(cls):
        """Configuración antes de ejecutar los tests"""
        print("\n🔄 Configurando tests de integración...")
        cls.verify_system_running()
    
    @classmethod
    def verify_system_running(cls):
        """Verificar que el sistema esté corriendo"""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Sistema detectado y funcionando")
            else:
                pytest.skip("Sistema no disponible para tests de integración")
        except requests.exceptions.RequestException:
            pytest.skip("Sistema no disponible para tests de integración")
    
    def test_health_endpoint(self):
        """Test del endpoint de health check"""
        response = requests.get(f"{BASE_URL}/health", timeout=API_TIMEOUT)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data
    
    def test_api_stats_endpoint(self):
        """Test del endpoint de estadísticas"""
        response = requests.get(f"{BASE_URL}/api/stats", timeout=API_TIMEOUT)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estructura de respuesta
        assert "total_employees" in data
        assert "departments" in data
        assert "avg_salary" in data
        assert "new_hires_this_month" in data
        
        # Verificar tipos de datos
        assert isinstance(data["total_employees"], int)
        assert isinstance(data["departments"], dict)
        assert isinstance(data["avg_salary"], (int, float))
        assert isinstance(data["new_hires_this_month"], int)
        
        # Verificar valores lógicos
        assert data["total_employees"] >= 0
        assert data["avg_salary"] >= 0
        assert data["new_hires_this_month"] >= 0
    
    def test_api_employees_endpoint(self):
        """Test del endpoint de empleados"""
        response = requests.get(f"{BASE_URL}/api/employees", timeout=API_TIMEOUT)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        
        if data:  # Si hay empleados
            employee = data[0]
            required_fields = ["id", "name", "department", "salary", "hire_date"]
            
            for field in required_fields:
                assert field in employee, f"Campo {field} faltante en empleado"
            
            # Verificar tipos
            assert isinstance(employee["id"], int)
            assert isinstance(employee["name"], str)
            assert isinstance(employee["department"], str)
            assert isinstance(employee["salary"], (int, float))
            assert isinstance(employee["hire_date"], str)
            
            # Verificar valores lógicos
            assert employee["salary"] > 0
            assert len(employee["name"]) > 0
            assert len(employee["department"]) > 0

# ========================================
# CONFIGURACIÓN DE PYTEST
# ========================================

def pytest_configure(config):
    """Configuración global de pytest"""
    print("\n🧪 Iniciando Tests de Integración - Sistema HR ETL")
    print("=" * 60)

def pytest_unconfigure(config):
    """Limpieza después de los tests"""
    print("\n✅ Tests de Integración Completados")
    print("=" * 60)