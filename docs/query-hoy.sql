SELECT count(*) FROM _tmp_bot_080920 LIMIT 1;

ALTER TABLE _tmp_bot_080920 add column `Numero Asesor` varchar(100);
ALTER TABLE _tmp_bot_080920 add column `Asesor` varchar(100);
ALTER TABLE _tmp_bot_080920 CHANGE `COD_CLIENTE` `idcliente` varchar(100);
-- OR
ALTER TABLE _tmp_bot_080920 CHANGE `codigo` `idcliente` varchar(100);

-- .
CREATE TABLE _tmp_mibanco_sobre_out_080920
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
    _tmp_bot_080920 t
        INNER JOIN
    BOT20_PRUEBA_DATA c ON t.idcliente = c.CODIGO_CLIENTE


SELECT count(*) FROM _tmp_mibanco_sobre_out_080920;



