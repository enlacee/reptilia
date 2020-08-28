# Carga miBanco

* [Documentación Carga MiBanco bot](docs/01-carga-mibanco.md)



### Requisitos ideales

	* SO Linux Ubuntu 18
	* Conexion VPN por openfortivpn
	* Motor base de datos NaviCat v15
	* LibreOffice 6.4 Calc
	* Block de Notas


### 01: Conectar a la base de datos: 
	
	server: 192.168.20.150:3306
	db: bda_sion
	user: root
	password: *****


### 02: Importar y crea tabla Automatico de los datos del archivo **BOT_26.xlsx** con el nombre **_tmp_bot_260820** que es el formato DD-MM-YY.

	NAVICAT
		database: dba_sion
		tables -> import wizard
			target_table = _tmp_bot_260820


### 03: Verificar si la tabla fue creada
	
```SQL
SELECT * FROM _tmp_bot_260820 LIMIT 1;
```

### 04: Crear campos y tabla: **_tmp_mibanco_sobre_out_26**
` Dia referencia se extrae del archivo **BOT_26.xlsx** es = 26`
` Ojo que el campo PROXIMO_VENCIMIENTO = 27. Se le suma 1 dia`

```SQL
ALTER TABLE _tmp_bot_260820 add column `Numero Asesor` varchar(100);
ALTER TABLE _tmp_bot_260820 add column `Asesor` varchar(100);
ALTER TABLE _tmp_bot_260820 CHANGE `COD_CLIENTE` `idcliente` varchar(100);
```

Esta siguiente sentencia no tiene (punto y coma) `;`.
Esto es para que creé la tabla y la siguiente consulta SQL  
lo cargue en la tabla automaticamente.

```SQL
CREATE TABLE _tmp_mibanco_sobre_out_26
SELECT 
    c.DOCUMENTO codigo,
    c.NOMBRE_CLIENTE nombre,
    'pen' moneda,
    c.saldo_soles monto,
    c.producto,
    c.nro_celular numero,
    c.nro_celular numero_act,
    c.PROXIMO_VENCIMIENTO fecha,
    t.`Numero Asesor` numero_asesor,
    t.asesor
FROM
    _tmp_bot_260820 t
        INNER JOIN
    BOT20_PRUEBA_DATA c ON t.idcliente = c.CODIGO_CLIENTE
WHERE
    c.PROXIMO_VENCIMIENTO = '2020-08-27';
```

### 05: Ahora verifica si los registros fueron creados en la tabla con los registros

```SQL
SELECT count(*) FROM _tmp_mibanco_sobre_out_26;
```

### 06: Exportar archivo en formato .xlsx

	NAVICAT
		dba_sion
		tables -> export wizard like file .txt
		- abrir excel LIBREOFFICE (copiar del .txt al libreooffice file) y guardar archivo como  
		  _tmp_mibanco_sobre_out_26.xlsx

`revisar los campos critos del archivo _tmp_mibanco_sobre_out_26.xlsx` 

	monto = en decimales
	fecha = formato Y-m-d -> 2020-08-27

### 07: Aplicación web: Hacer la carga de data
	
	URL=http://172.16.20.7:5000/
	user: alvaro
	password: *****

### 08: Configurar DASHBOARD

Seleccionar la empresa en el **ComboBox empresas** [ubicado en el header a la derecha].

	ComboBoxEmpresas = MiBanco Sobreendeudamiento

### 09: Crear una lista

Ir al menu hamburguesa:

	-> LISTA
		-> ico agregar 
			-> 80 = identificado de mibanco
			-> ID = 80260820
			-> NOMBRE = MiBancoSobrendeudamiento80260820
			-> CAMPAÑA = mibanco_sobre_endeudamientos
                    
### 10: Crear una carga
Ir al menu hamburguesa:

	-> CARGA
    	-> ico agregar 
			-> CANAL = CALL
			-> LISTA = mibanco_sobre_endeudamientos
			-> PROVEEDOR = Fravatel
			-> SUBIR ARCHIVO (buscar archivo .xlsx)
                - relacionar los campos
				sitema					file.xlsx
				TELEFONOS				NUMERO_ACT
                                    
                - presina escape (para salir de la ventana) (improve this options SYS)


### 11: Verificar datos cargados: en el server MiBancoBOT

	server: 172.16.80.5:3306
	db: mibanco
	user: root
	password: *****

```SQL
select * from tbl_client_data where list_id = 80260820;
select * from tbl_client_data where list_id = 70270820 AND client_id like "%3338938%"
```

Aquí verificar cuantos registros se guardarón y verificar algún registro para mayor seguridad.
Verficar los siguientes campos

	client_id	-> que coincida al nombre de usuario del excel
	create_at   -> fecha hoy registrado
	list_id		-> id de lista.
