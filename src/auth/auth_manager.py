import hashlib
import secrets
from typing import Optional, Dict
from ..database.neon_db import NeonDB

class AuthManager:
    def __init__(self):
        try:
            self.db = NeonDB()
            self.create_auth_tables()
            self.sessions = {}
        except Exception as e:
            print(f"Error inicializando AuthManager: {e}")
            self.db = None
            self.sessions = {}
    
    def create_auth_tables(self):
        """Crea tablas de usuarios y sesiones"""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    # Crear tabla users
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            username VARCHAR(50) UNIQUE NOT NULL,
                            email VARCHAR(100) UNIQUE NOT NULL,
                            password_hash VARCHAR(255) NOT NULL,
                            role VARCHAR(20) DEFAULT 'user',
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Crear tabla projects
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS projects (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(255) NOT NULL,
                            description TEXT,
                            user_id INTEGER REFERENCES users(id),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    conn.commit()
                    
                    # Insertar usuario admin
                    try:
                        cur.execute("""
                            INSERT INTO users (username, email, password_hash, role)
                            VALUES ('admin', 'admin@montecarlo.com', %s, 'admin')
                            ON CONFLICT (username) DO NOTHING
                        """, (self.hash_password('admin123'),))
                        conn.commit()
                    except Exception as e:
                        print(f"Usuario admin ya existe o error: {e}")
                        
        except Exception as e:
            print(f"Error creando tablas de autenticación: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hash de contraseña"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self, username: str, password: str) -> Optional[Dict]:
        """Autenticar usuario"""
        if not self.db:
            return None
            
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, username, email, role FROM users 
                        WHERE username = %s AND password_hash = %s
                    """, (username, self.hash_password(password)))
                    
                    user = cur.fetchone()
                    if user:
                        session_id = secrets.token_hex(16)
                        user_data = {
                            'id': user[0],
                            'username': user[1],
                            'email': user[2],
                            'role': user[3]
                        }
                        self.sessions[session_id] = user_data
                        return {'session_id': session_id, 'user': user_data}
                    return None
        except Exception as e:
            print(f"Error en login: {e}")
            return None
    
    def get_user_projects(self, user_id: int):
        """Obtener proyectos del usuario"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT p.id, p.name, p.description, p.created_at,
                           COUNT(s.id) as scenario_count
                    FROM projects p
                    LEFT JOIN scenarios s ON p.id = s.project_id
                    WHERE p.user_id = %s
                    GROUP BY p.id, p.name, p.description, p.created_at
                    ORDER BY p.created_at DESC
                """, (user_id,))
                
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]