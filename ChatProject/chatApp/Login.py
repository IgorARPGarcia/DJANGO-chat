import mysql.connector
import bcrypt

# Configurações do banco de dados
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "senhaSenha",
    "database": "login_seguro"
}

# Cria o banco de dados e a tabela se não existir
def inicializar_banco():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS login_seguro")
        cursor.close()
        conn.close()

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            )
        """)
        conn.commit()
    except mysql.connector.Error as err:
        print("Erro ao inicializar banco:", err)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Cadastra um novo usuário
def criar_usuario(username, password):
    print(f"Registrando usuário: {username}")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO usuarios (username, password) VALUES (%s, %s)",
                       (username, hashed.decode('utf-8')))
        conn.commit()
        print("Usuário registrado no banco.")
        return True
    except mysql.connector.IntegrityError:
        return False  # Usuário já existe
    except mysql.connector.Error as err:
        print(f"Erro ao cadastrar: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

# Autentica um usuário existente
def autenticar_usuario(username, password):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("SELECT password FROM usuarios WHERE username = %s", (username,))
        resultado = cursor.fetchone()

        if resultado and bcrypt.checkpw(password.encode('utf-8'), resultado[0].encode('utf-8')):
            return True
        else:
            return False
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ou consultar: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

# Inicializa o banco ao importar
inicializar_banco()
