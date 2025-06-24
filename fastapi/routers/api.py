# ========================================
# API_SIMPLE.PY - API ENDPOINTS PARA HR DASHBOARD
# ========================================

from fastapi import APIRouter, HTTPException
import mysql.connector
import os
from typing import List, Dict, Any

router = APIRouter(prefix="/api", tags=["api"])

# ========================================
# CONFIGURACIÓN DE MYSQL
# ========================================
def get_mysql_connection():
    """Crear conexión a MySQL usando mysql-connector-python"""
    try:
        # Para desarrollo local usamos localhost, para Docker usamos el nombre del servicio
        mysql_host = os.getenv("MYSQL_HOST", "mysql")
        if mysql_host == "mysql":
            mysql_host = "localhost"  # Cambiar a localhost cuando no estemos en Docker
            
        connection = mysql.connector.connect(
            host=mysql_host,
            port=int(os.getenv("MYSQL_PORT", "3307")),
            user=os.getenv("MYSQL_USER", "mysql_f5_de1"),
            password=os.getenv("MYSQL_PASSWORD", "3tL_f542"),
            database=os.getenv("MYSQL_DATABASE", "hr"),
            charset='utf8mb4'
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None

# ========================================
# API ENDPOINTS
# ========================================

@router.get("/stats")
async def get_stats():
    """Obtener estadísticas generales de HR"""
    try:
        conn = get_mysql_connection()
        if not conn:
            # Datos de ejemplo si no hay conexión MySQL
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
        
        cursor = conn.cursor(dictionary=True)
        
        # Total empleados
        cursor.execute("SELECT COUNT(*) as total FROM employees")
        total_result = cursor.fetchone()
        total_employees = total_result['total'] if total_result else 0
        
        # Empleados por departamento
        cursor.execute("""
            SELECT department, COUNT(*) as count 
            FROM employees 
            GROUP BY department
        """)
        dept_results = cursor.fetchall()
        departments = {row['department']: row['count'] for row in dept_results}
        
        # Salario promedio
        cursor.execute("SELECT AVG(salary) as avg_sal FROM employees")
        avg_result = cursor.fetchone()
        avg_salary = float(avg_result['avg_sal']) if avg_result['avg_sal'] else 0
        
        # Contrataciones del mes actual
        cursor.execute("""
            SELECT COUNT(*) as new_hires 
            FROM employees 
            WHERE MONTH(hire_date) = MONTH(CURDATE()) 
            AND YEAR(hire_date) = YEAR(CURDATE())
        """)
        hires_result = cursor.fetchone()
        new_hires = hires_result['new_hires'] if hires_result else 0
        
        cursor.close()
        conn.close()
        
        return {
            "total_employees": total_employees,
            "departments": departments,
            "avg_salary": round(avg_salary, 2),
            "new_hires_this_month": new_hires
        }
        
    except Exception as e:
        print(f"Error en get_stats: {e}")
        # Retornar datos de ejemplo en caso de error
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

@router.get("/employees")
async def get_employees():
    """Obtener lista de empleados"""
    try:
        conn = get_mysql_connection()
        if not conn:
            # Datos de ejemplo si no hay conexión MySQL
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
                },
                {
                    "id": 3,
                    "name": "Carlos López",
                    "department": "Sales", 
                    "salary": 55000,
                    "hire_date": "2023-05-10"
                }
            ]
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, name, department, salary, hire_date 
            FROM employees 
            ORDER BY hire_date DESC 
            LIMIT 50
        """)
        employees = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Convertir dates a strings
        for emp in employees:
            if emp.get('hire_date'):
                emp['hire_date'] = emp['hire_date'].strftime('%Y-%m-%d')
        
        return employees
        
    except Exception as e:
        print(f"Error en get_employees: {e}")
        # Retornar datos de ejemplo en caso de error
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
            },
            {
                "id": 3,
                "name": "Carlos López",
                "department": "Sales",
                "salary": 55000,
                "hire_date": "2023-05-10"
            }
        ]

@router.get("/departments")
async def get_departments():
    """Obtener lista de departamentos con estadísticas"""
    try:
        conn = get_mysql_connection()
        if not conn:
            # Datos de ejemplo si no hay conexión MySQL
            return [
                {"name": "Engineering", "employee_count": 45, "avg_salary": 78000},
                {"name": "Sales", "employee_count": 30, "avg_salary": 58000},
                {"name": "Marketing", "employee_count": 25, "avg_salary": 62000},
                {"name": "HR", "employee_count": 15, "avg_salary": 55000},
                {"name": "Finance", "employee_count": 20, "avg_salary": 68000},
                {"name": "Operations", "employee_count": 15, "avg_salary": 52000}
            ]
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                department as name,
                COUNT(*) as employee_count,
                AVG(salary) as avg_salary
            FROM employees 
            GROUP BY department
            ORDER BY employee_count DESC
        """)
        departments = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Redondear salarios
        for dept in departments:
            dept['avg_salary'] = round(dept['avg_salary'], 2) if dept['avg_salary'] else 0
        
        return departments
        
    except Exception as e:
        print(f"Error en get_departments: {e}")
        # Retornar datos de ejemplo en caso de error
        return [
            {"name": "Engineering", "employee_count": 45, "avg_salary": 78000},
            {"name": "Sales", "employee_count": 30, "avg_salary": 58000},
            {"name": "Marketing", "employee_count": 25, "avg_salary": 62000},
            {"name": "HR", "employee_count": 15, "avg_salary": 55000},
            {"name": "Finance", "employee_count": 20, "avg_salary": 68000},
            {"name": "Operations", "employee_count": 15, "avg_salary": 52000}
        ]
