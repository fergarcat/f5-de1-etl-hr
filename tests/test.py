#
async def api_health():
    """Health check de la API y conexiones"""
    health_status = {
        "api": "healthy",
        "timestamp": datetime.now().isoformat(),
        "databases": {}
    }
    
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
        health_status["databases"]["mysql"] = "connected"
    except:
        health_status["databases"]["mysql"] = "error"
    
    
    try:
        db = get_mongodb_connection()
        # Test básico de conexión
        db.list_collection_names()
        health_status["databases"]["mongodb"] = "connected"
    except:
        health_status["databases"]["mongodb"] = "error"
    
    # Test Redis
    try:
        r = get_redis_connection()
        r.ping()
        health_status["databases"]["redis"] = "connected"
    except:
        health_status["databases"]["redis"] = "error"
    
    return health_status
#