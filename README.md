# Proyecto final de desarrollo de software

# Integrantes

-   
-   
-   

# Arquitectura de proyecto

## Backend - Flask


## Frontend - React

# Ejecutar proyecto

## Backend

Para ejecutar el backend es necesario python 3.11 o superior. en la carpeta `/backend`
es necesario instalar dependencias
```bash
cd backend
python -m venv venv
# Activar entorno
venv\Scripts\activate
pip install -r requirements.txt
```

Ejecutar migraciones

```bash
# con el entorno activado
flask db upgrade
# Generar usuarios por defecto
flask seed
```


Activar entorno y ejecutar el proyecto

```bash
# con el entorno activado
python run.py
```

### Documentación de la API

Una vez el servidor este corriendo, la documentación se encuentra en [/docs/scalar](http://127.0.0.1:5000/docs/scalar)

## Frontend

Instalar dependencias

```bash
npm install
```

Ejecutar el proyecto

```bash
npm run dev
```
