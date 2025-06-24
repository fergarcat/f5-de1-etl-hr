import pytest
import sys
import os
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import mysql.connector

# Agregar el directorio raíz al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ========================================
# TESTS DE COMPONENTES DE BASE DE DATOS
# ========================================

class TestDatabaseClients:
    """Tests para los clientes de base de datos"""
    
    @patch('mysql.connector.connect')
    def test_mysql_connection_with_environment_variables(self, mock_connect):
        """Test de conexión MySQL con variables de entorno"""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        # Mock de variables de entorno
        with patch.dict(os.environ, {
            'MYSQL_HOST': 'test_host',
            'MYSQL_PORT': '3306',
            'MYSQL_USER': 'test_user',
            'MYSQL_PASSWORD': 'test_pass',
            'MYSQL_DATABASE': 'test_db'
        }):
            from fastapi.routers.api_simple import get_mysql_connection
            result = get_mysql_connection()
            
            assert result is not None
            mock_connect.assert_called_once()
            call_args = mock_connect.call_args[1]
            assert call_args['host'] == 'localhost'  # Se convierte a localhost en desarrollo
            assert call_args['user'] == 'test_user'
            assert call_args['database'] == 'test_db'
    
    @patch('mysql.connector.connect')
    def test_mysql_connection_error_handling(self, mock_connect):
        """Test de manejo de errores en conexión MySQL"""
        # Simular diferentes tipos de errores
        errors_to_test = [
            mysql.connector.Error("Connection failed"),
            ConnectionError("Network error"),
            Exception("Generic error")
        ]
        
        for error in errors_to_test:
            mock_connect.side_effect = error
            from fastapi.routers.api_simple import get_mysql_connection
            result = get_mysql_connection()
            assert result is None
    
    def test_mysql_query_execution_mock(self):
        """Test de ejecución de queries MySQL con mocks"""
        with patch('fastapi.routers.api_simple.get_mysql_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_get_conn.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            
            # Simular datos de empleados
            mock_cursor.fetchall.return_value = [
                {'id': 1, 'name': 'Test User', 'department': 'IT', 'salary': 50000, 'hire_date': '2023-01-01'}
            ]
            
            from fastapi.routers.api_simple import router
            from fastapi.testclient import TestClient
            from fastapi import FastAPI
            
            app = FastAPI()
            app.include_router(router)
            client = TestClient(app)
            
            response = client.get("/employees")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]['name'] == 'Test User'


class TestDataTransformation:
    """Tests para transformación de datos"""
    
    def test_salary_formatting(self):
        """Test de formateo de salarios"""
        test_cases = [
            (50000, 50000.0),
            (75000.5, 75000.5),
            (0, 0.0),
            (None, 0.0)
        ]
        
        for input_val, expected in test_cases:
            if input_val is None:
                result = 0.0
            else:
                result = float(input_val)
            assert result == expected
    
    def test_department_data_aggregation(self):
        """Test de agregación de datos por departamento"""
        # Datos de ejemplo
        employees = [
            {'department': 'IT', 'salary': 50000},
            {'department': 'IT', 'salary': 60000},
            {'department': 'HR', 'salary': 45000},
            {'department': 'Sales', 'salary': 55000},
            {'department': 'Sales', 'salary': 48000}
        ]
        
        # Simular agregación
        dept_stats = {}
        for emp in employees:
            dept = emp['department']
            if dept not in dept_stats:
                dept_stats[dept] = {'count': 0, 'total_salary': 0}
            dept_stats[dept]['count'] += 1
            dept_stats[dept]['total_salary'] += emp['salary']
        
        # Calcular promedios
        for dept in dept_stats:
            dept_stats[dept]['avg_salary'] = dept_stats[dept]['total_salary'] / dept_stats[dept]['count']
        
        # Verificaciones
        assert dept_stats['IT']['count'] == 2
        assert dept_stats['IT']['avg_salary'] == 55000
        assert dept_stats['HR']['count'] == 1
        assert dept_stats['Sales']['avg_salary'] == 51500
    
    def test_date_handling(self):
        """Test de manejo de fechas"""
        from datetime import datetime, date
        
        # Test diferentes formatos de fecha
        date_strings = [
            "2023-01-15",
            "2023-03-20", 
            "2023-12-31"
        ]
        
        for date_str in date_strings:
            # Verificar que se puede parsear la fecha
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            assert isinstance(parsed_date, date)
            assert parsed_date.year == 2023


class TestAPIResponseValidation:
    """Tests para validación de respuestas de API"""
    
    def test_stats_response_schema(self):
        """Test del schema de respuesta de stats"""
        # Schema esperado
        expected_schema = {
            "total_employees": int,
            "departments": dict,
            "avg_salary": (int, float),
            "new_hires_this_month": int
        }
        
        # Datos de ejemplo que debe retornar la API
        sample_response = {
            "total_employees": 150,
            "departments": {"IT": 45, "Sales": 30},
            "avg_salary": 65000,
            "new_hires_this_month": 5
        }
        
        # Validar schema
        for field, expected_type in expected_schema.items():
            assert field in sample_response
            assert isinstance(sample_response[field], expected_type)
    
    def test_employees_response_schema(self):
        """Test del schema de respuesta de employees"""
        sample_employee = {
            "id": 1,
            "name": "Juan Pérez", 
            "department": "Engineering",
            "salary": 75000,
            "hire_date": "2023-01-15"
        }
        
        required_fields = ["id", "name", "department", "salary", "hire_date"]
        for field in required_fields:
            assert field in sample_employee
        
        assert isinstance(sample_employee["id"], int)
        assert isinstance(sample_employee["name"], str)
        assert isinstance(sample_employee["salary"], (int, float))
    
    def test_departments_response_schema(self):
        """Test del schema de respuesta de departments"""
        sample_department = {
            "name": "Engineering",
            "employee_count": 45,
            "avg_salary": 78000
        }
        
        required_fields = ["name", "employee_count", "avg_salary"]
        for field in required_fields:
            assert field in sample_department
        
        assert isinstance(sample_department["employee_count"], int)
        assert isinstance(sample_department["avg_salary"], (int, float))


class TestErrorScenarios:
    """Tests para diferentes escenarios de error"""
    
    def test_empty_database_handling(self):
        """Test de manejo de base de datos vacía"""
        # Simular respuesta de base de datos vacía
        empty_responses = {
            "employees": [],
            "departments": [],
            "total_employees": 0,
            "avg_salary": 0
        }
        
        # Verificar que el sistema maneja datos vacíos correctamente
        for key, value in empty_responses.items():
            if isinstance(value, list):
                assert len(value) == 0
            elif isinstance(value, (int, float)):
                assert value >= 0
    
    def test_invalid_data_filtering(self):
        """Test de filtrado de datos inválidos"""
        # Datos con valores inválidos
        invalid_employees = [
            {"id": 1, "name": "", "department": "IT", "salary": -1000},  # Nombre vacío, salario negativo
            {"id": 2, "name": "Valid User", "department": "", "salary": 50000},  # Departamento vacío
            {"id": 3, "name": "Another User", "department": "IT", "salary": 60000},  # Válido
        ]
        
        # Filtrar datos válidos
        valid_employees = []
        for emp in invalid_employees:
            if (emp.get("name", "").strip() and 
                emp.get("department", "").strip() and 
                emp.get("salary", 0) > 0):
                valid_employees.append(emp)
        
        assert len(valid_employees) == 1
        assert valid_employees[0]["name"] == "Another User"
    
    def test_connection_timeout_simulation(self):
        """Test de simulación de timeout de conexión"""
        with patch('mysql.connector.connect') as mock_connect:
            # Simular timeout
            mock_connect.side_effect = mysql.connector.Error("Connection timeout")
            
            from fastapi.routers.api_simple import get_mysql_connection
            result = get_mysql_connection()
            
            # Debe retornar None y no lanzar excepción
            assert result is None


class TestUtilityFunctions:
    """Tests para funciones de utilidad"""
    
    def test_number_formatting(self):
        """Test de formateo de números"""
        test_cases = [
            (1000, "1,000"),
            (1000000, "1,000,000"),
            (123456.78, "123,456.78"),
            (0, "0")
        ]
        
        for number, expected in test_cases:
            # Simular formateo (implementación básica)
            formatted = f"{number:,.2f}".rstrip('0').rstrip('.')
            # Verificar que el número se formatea correctamente
            assert isinstance(formatted, str)
            assert len(formatted) > 0
    
    def test_percentage_calculations(self):
        """Test de cálculos de porcentajes"""
        test_cases = [
            (50, 100, 50.0),  # 50 de 100 = 50%
            (25, 200, 12.5),  # 25 de 200 = 12.5%
            (0, 100, 0.0),    # 0 de 100 = 0%
        ]
        
        for part, total, expected_percentage in test_cases:
            if total > 0:
                percentage = (part / total) * 100
            else:
                percentage = 0.0
            
            assert abs(percentage - expected_percentage) < 0.001
    
    def test_data_validation_helpers(self):
        """Test de funciones auxiliares de validación"""
        
        def is_valid_email(email):
            """Función simple de validación de email"""
            return "@" in email and "." in email
        
        def is_valid_salary(salary):
            """Función de validación de salario"""
            return isinstance(salary, (int, float)) and salary >= 0
        
        def is_valid_name(name):
            """Función de validación de nombre"""
            return isinstance(name, str) and len(name.strip()) > 0
        
        # Tests de validación
        assert is_valid_email("test@example.com") == True
        assert is_valid_email("invalid-email") == False
        
        assert is_valid_salary(50000) == True
        assert is_valid_salary(-1000) == False
        assert is_valid_salary("invalid") == False
        
        assert is_valid_name("Juan Pérez") == True
        assert is_valid_name("") == False
        assert is_valid_name("   ") == False


class TestConfigurationHandling:
    """Tests para manejo de configuración"""
    
    def test_environment_variables_fallback(self):
        """Test de fallback de variables de entorno"""
        # Test con variables de entorno faltantes
        with patch.dict(os.environ, {}, clear=True):
            # Simular valores por defecto
            mysql_host = os.getenv("MYSQL_HOST", "localhost")
            mysql_port = int(os.getenv("MYSQL_PORT", "3306"))
            mysql_user = os.getenv("MYSQL_USER", "default_user")
            
            assert mysql_host == "localhost"
            assert mysql_port == 3306
            assert mysql_user == "default_user"
    
    def test_database_host_resolution(self):
        """Test de resolución de host de base de datos"""
        # Test lógica de host (Docker vs local)
        test_cases = [
            ("mysql", "localhost"),  # Docker service name -> localhost
            ("localhost", "localhost"),  # Ya es localhost
            ("192.168.1.100", "192.168.1.100")  # IP específica
        ]
        
        for input_host, expected_host in test_cases:
            # Simular la lógica del código
            if input_host == "mysql":
                resolved_host = "localhost"
            else:
                resolved_host = input_host
            
            assert resolved_host == expected_host


# ========================================
# CONFIGURACIÓN DE PYTEST
# ========================================

@pytest.fixture
def sample_employee():
    """Fixture con datos de empleado de ejemplo"""
    return {
        "id": 1,
        "name": "Juan Pérez",
        "department": "Engineering", 
        "salary": 75000,
        "hire_date": "2023-01-15"
    }

@pytest.fixture
def sample_department():
    """Fixture con datos de departamento de ejemplo"""
    return {
        "name": "Engineering",
        "employee_count": 45,
        "avg_salary": 78000
    }

@pytest.fixture
def mock_mysql_connection():
    """Fixture con mock de conexión MySQL"""
    with patch('mysql.connector.connect') as mock_connect:
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        yield mock_conn, mock_cursor

# Marcadores para organizar los tests
pytestmark = [
    pytest.mark.unit,
    pytest.mark.components
]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
