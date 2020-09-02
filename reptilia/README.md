
# Reptilia

### Requisitos

	1. Ubuntu 18.04
	2. python3.8, pip3.8 (like enviroment)
	3. 

### Instalation

Descargar y descomprimir el proyecto llamado **projects**

	cd projects

Crear el entorno virtual para trabajar con python 3.8 y activar el entorno.

	virtualenv reptilia/ -p python3.8
	source reptilia/bin/activate

Instalar los paquetes del proyecto.

	bin/pip3.8 install -r requirements.txt

Cambiar la direccion host en `run.py`  
Current ip on LAN: example: 192.168.1.22

	socketio.run(app, host= "192.168.1.22")

Cargar el servidor:

	python3.8 run.py

