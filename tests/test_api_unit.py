# ========================================
# TEST_API_UNIT.PY - TESTS UNITARIOS PARA APIs
# ========================================

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
import json

# Agregar el directorio raíz al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar desde el proyecto
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fastapi'))

from main import app
from routers.api import get_mysql_connection

# ========================================
# CONFIGURACIÓN DE TESTS
# ========================================

client = TestClient(app)

class TestAPIEndpoints:
    """Tests unitarios para los endpoints de la API"""
    
    def test_root_endpoint(self):
        """Test del endpoint raíz que devuelve el dashboard"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        
    def test_analytics_endpoint(self):
        """Test del endpoint de analytics"""
        response = client.get("/analytics")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    @patch('fastapi.routers.api_simple.get_mysql_connection')
    def test_api_stats_success(self, mock_mysql):
        """Test del endpoint /api/stats con conexión exitosa a MySQL"""
        # Mock de la conexión MySQL exitosa
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_mysql.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Configurar los resultados del cursor
        mock_cursor.fetchone.side_effect = [
            {'total': 150},  # Total empleados
            {'avg_sal': 65000.0},  # Salario promedio
            {'new_hires': 5}  # Nuevas contrataciones
        ]
        mock_cursor.fetchall.return_value = [
            {'department': 'Engineering', 'count': 45},
            {'department': 'Sales', 'count': 30},
            {'department': 'Marketing', 'count': 25}
        ]
        
        response = client.get("/api/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_employees"] == 150
        assert data["avg_salary"] == 65000.0
        assert data["new_hires_this_month"] == 5
        assert "departments" in data
        assert data["departments"]["Engineering"] == 45
    
    @patch('fastapi.routers.api_simple.get_mysql_connection')
    def test_api_stats_fallback(self, mock_mysql):
        """Test del endpoint /api/stats con fallback cuando falla MySQL"""
        # Mock de conexión fallida
        mock_mysql.return_value = None
        
        response = client.get("/api/stats")
        
        assert response.status_code == 200
        data = response.json()
        # Verificar que retorna datos de ejemplo
        assert data["total_employees"] == 150
        assert data["avg_salary"] == 65000
        assert "departments" in data
        assert len(data["departments"]) > 0
    
    @patch('fastapi.routers.api_simple.get_mysql_connection')
    def test_api_employees_success(self, mock_mysql):
        """Test del endpoint /api/employees con conexión exitosa"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_mysql.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'name': 'Juan Pérez',
                'department': 'Engineering',
                'salary': 75000,
                'hire_date': '2023-01-15'
            },
            {
                'id': 2,
                'name': 'María García',
                'department': 'Marketing',
                'salary': 65000,
                'hire_date': '2023-03-20'
            }
        ]
        
        response = client.get("/api/employees")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Juan Pérez"
        assert data[0]["department"] == "Engineering"
        assert data[0]["salary"] == 75000
    
    @patch('fastapi.routers.api_simple.get_mysql_connection')
    def test_api_employees_fallback(self, mock_mysql):
        """Test del endpoint /api/employees con fallback"""
        mock_mysql.return_value = None
        
        response = client.get("/api/employees")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3  # Datos de ejemplo mínimos
        assert all("name" in emp for emp in data)
        assert all("department" in emp for emp in data)
    
    @patch('fastapi.routers.api_simple.get_mysql_connection')
    def test_api_departments_success(self, mock_mysql):
        """Test del endpoint /api/departments con conexión exitosa"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_mysql.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [
            {'name': 'Engineering', 'employee_count': 45, 'avg_salary': 78000.0},
            {'name': 'Sales', 'employee_count': 30, 'avg_salary': 58000.0},
            {'name': 'Marketing', 'employee_count': 25, 'avg_salary': 62000.0}
        ]
        
        response = client.get("/api/departments")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["name"] == "Engineering"
        assert data[0]["employee_count"] == 45
        assert data[0]["avg_salary"] == 78000.0
    
    @patch('fastapi.routers.api_simple.get_mysql_connection')
    def test_api_departments_fallback(self, mock_mysql):
        """Test del endpoint /api/departments con fallback"""
        mock_mysql.return_value = None
        
        response = client.get("/api/departments")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 6  # Datos de ejemplo mínimos
        assert all("name" in dept for dept in data)
        assert all("employee_count" in dept for dept in data)
        assert all("avg_salary" in dept for dept in data)
    
    def test_static_files_access(self):
        """Test de acceso a archivos estáticos"""
        # Test CSS
        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        assert "text/css" in response.headers["content-type"]
        
        # Test JavaScript
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "application/javascript" in response.headers["content-type"] or "text/javascript" in response.headers["content-type"]


class TestDatabaseConnections:
    """Tests unitarios para las conexiones de base de datos"""
    
    @patch('mysql.connector.connect')
    def test_mysql_connection_success(self, mock_connect):
        """Test de conexión exitosa a MySQL"""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        from fastapi.routers.api_simple import get_mysql_connection
        result = get_mysql_connection()
        
        assert result is not None
        mock_connect.assert_called_once()
    
    @patch('mysql.connector.connect')
    def test_mysql_connection_failure(self, mock_connect):
        """Test de fallo en conexión a MySQL"""
        mock_connect.side_effect = Exception("Connection failed")
        
        from fastapi.routers.api_simple import get_mysql_connection
        result = get_mysql_connection()
        
        assert result is None


class TestDataValidation:
    """Tests para validación de datos"""
    
    def test_stats_data_structure(self):
        """Test de estructura de datos del endpoint stats"""
        response = client.get("/api/stats")
        data = response.json()
        
        # Verificar campos requeridos
        required_fields = ["total_employees", "departments", "avg_salary", "new_hires_this_month"]
        for field in required_fields:
            assert field in data, f"Campo {field} faltante en respuesta"
        
        # Verificar tipos de datos
        assert isinstance(data["total_employees"], int)
        assert isinstance(data["departments"], dict)
        assert isinstance(data["avg_salary"], (int, float))
        assert isinstance(data["new_hires_this_month"], int)
    
    def test_employees_data_structure(self):
        """Test de estructura de datos del endpoint employees"""
        response = client.get("/api/employees")
        data = response.json()
        
        assert isinstance(data, list)
        if len(data) > 0:
            employee = data[0]
            required_fields = ["id", "name", "department", "salary", "hire_date"]
            for field in required_fields:
                assert field in employee, f"Campo {field} faltante en empleado"
    
    def test_departments_data_structure(self):
        """Test de estructura de datos del endpoint departments"""
        response = client.get("/api/departments")
        data = response.json()
        
        assert isinstance(data, list)
        if len(data) > 0:
            department = data[0]
            required_fields = ["name", "employee_count", "avg_salary"]
            for field in required_fields:
                assert field in department, f"Campo {field} faltante en departamento"
            
            assert isinstance(department["employee_count"], int)
            assert isinstance(department["avg_salary"], (int, float))


class TestErrorHandling:
    """Tests para manejo de errores"""
    
    def test_nonexistent_endpoint(self):
        """Test de endpoint inexistente"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_static_file(self):
        """Test de archivo estático inexistente"""
        response = client.get("/static/nonexistent.css")
        assert response.status_code == 404
    
    @patch('fastapi.routers.api_simple.get_mysql_connection')
    def test_database_error_handling(self, mock_mysql):
        """Test de manejo de errores de base de datos"""
        # Simular error en la conexión
        mock_mysql.side_effect = Exception("Database error")
        
        response = client.get("/api/stats")
        # Debe retornar 200 con datos fallback, no error
        assert response.status_code == 200
        data = response.json()
        assert "total_employees" in data


# ========================================
# CONFIGURACIÓN DE PYTEST
# ========================================

@pytest.fixture
def test_client():
    """Fixture para cliente de test"""
    return TestClient(app)

@pytest.fixture
def sample_employee_data():
    """Fixture con datos de ejemplo de empleados"""
    return [
        {
            "id": 1,
            "name": "Juan Pérez",
            "department": "Engineering",
            "salary": 75000,
            "hire_date": "2023-01-15"
        },
        {
            "id": 2,
            "name": "María García",
            "department": "Marketing",
            "salary": 65000,
            "hire_date": "2023-03-20"
        }
    ]

@pytest.fixture
def sample_stats_data():
    """Fixture con datos de ejemplo de estadísticas"""
    return {
        "total_employees": 150,
        "departments": {
            "Engineering": 45,
            "Sales": 30,
            "Marketing": 25,
            "HR": 15,
            "Finance": 20,
            "Operations": 15
        },
        "avg_salary": 65000,
        "new_hires_this_month": 5
    }


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
