--1
SELECT
	p.*
FROM involucra i
INNER JOIN persona p
on i.personadni = p.dni
INNER JOIN rol r
on r.idrol = i.idrol
WHERE r.nombre_rol = 'Sospechoso';


--2
SELECT
	*
FROM persona
WHERE id_ubicacion IN (
	SELECT
		b.id_lugar
	FROM
		(
			SELECT DISTINCT
				u.id_lugar,
				i.idcaso
			FROM ubicacion u
			INNER JOIN persona p
			on p.id_ubicacion = u.id_lugar
			INNER JOIN involucra i
			on p.dni = i.personadni
			INNER JOIN rol r
			on i.idrol = r.idrol
			WHERE r.nombre_rol = 'Sospechoso'
			GROUP BY u.id_lugar, i.idcaso
		) as b
	GROUP BY b.id_lugar
	HAVING count(*) > 1
);
--3
SELECT
	*
FROM oficial o
WHERE o.dni IN (
	SELECT
		dni
	FROM oficial o
	INNER JOIN custodia cu
	on cu.oficialdni = o.dni
	INNER JOIN evidencia e
	on e.idevidencia = cu.idevidencia
	INNER JOIN caso c
	on c.idcaso = e.idcaso
	GROUP BY o.dni
	HAVING count(DISTINCT c.idcaso) > 1
);

--4
CREATE OR REPLACE FUNCTION sucesionEventos(inidcaso integer)
RETURNS TABLE(idevento integer, idcaso integer, personadni bigint, descripcion text, hora_evento time, fecha_evento date)
AS
$BODY$
SELECT
	e.idevento,
	e.idcaso,
	e.personadni,
	e.descripcion,
	e.hora_evento,
	e.fecha_evento
FROM evento e
WHERE e.idcaso = sucesionEventos.inidcaso
ORDER BY e.fecha_evento, e.hora_evento, e.personadni;
$BODY$
LANGUAGE sql;

--5
SELECT
    o.dni
FROM oficial o
INNER JOIN caso_resuelto cr
on cr.oficialresueltodni = o.dni
GROUP BY o.dni
HAVING count(DISTINCT cr.idcaso) IN
(
	SELECT
	    count(DISTINCT cr.idcaso) as CasosResueltos
	FROM oficial o
	INNER JOIN caso_resuelto cr
	on cr.oficialresueltodni = o.dni
	GROUP BY o.dni
	ORDER BY CasosResueltos desc
	LIMIT 1
);

--6
-- Asumimos que la ubicacion que se busca es la actual, quiere decir al ultimo lugar movido
CREATE OR REPLACE FUNCTION ubicacionesEvidencia (inidcaso integer)
RETURNS TABLE(idevidencia integer, id_lugar integer, id_calle integer, nro_calle integer, idloc integer, idprov integer, ultimo_movimiento date)
AS
$BODY$
SELECT
	cu.idevidencia,
	u.*,
	cu.ultimo_movimiento
FROM
	(
		SELECT
			e.idevidencia,
			MAX(c.fecha_custodia) as ultimo_movimiento
		FROM evidencia e
		INNER JOIN custodia c
		on c.idevidencia = e.idevidencia
		WHERE e.idcaso = ubicacionesEvidencia.inidcaso
		GROUP BY e.idevidencia
	) cu
INNER JOIN custodia c
ON cu.idevidencia = c.idevidencia AND cu.ultimo_movimiento = c.fecha_custodia
INNER JOIN ubicacion u
ON c.id_ubicacion = u.id_lugar
$BODY$
LANGUAGE sql;

--7
-- Asumimos que oficial involucrado incluye al que resolvio (si fue resuelto) y al principal
CREATE OR REPLACE FUNCTION oficialesCaso(inidcaso integer)
RETURNS TABLE(dni bigint, idservicio integer, iddepto integer, idrango integer, fecha_ingreso date, nroplaca integer, nro_escritorio integer)
AS
$BODY$
SELECT
	o.*
FROM oficial o
INNER JOIN involucra i
on o.dni = i.personadni
WHERE i.idcaso = oficialesCaso.inidcaso
UNION
SELECT
	o.*
FROM oficial o
INNER JOIN caso_resuelto cr
on o.dni = cr.oficialresueltodni
WHERE cr.idcaso = oficialesCaso.inidcaso
UNION
SELECT
	o.*
FROM oficial o
INNER JOIN caso c
on o.dni = c.oficialprincipaldni
WHERE c.idcaso = oficialesCaso.inidcaso
$BODY$
LANGUAGE sql;

--8
SELECT
	cat.idcat,
	cat.nombre_cat,
	count(c.idcaso) as CantidadCasos
FROM categoria cat
INNER JOIN caso c
on c.id_categoria = cat.idcat
GROUP BY cat.idcat, cat.nombre_cat
ORDER BY CantidadCasos DESC;


--9
CREATE OR REPLACE FUNCTION testimoniosCaso(inidcaso integer)
RETURNS TABLE(idtest integer, personadni bigint, idcaso integer, oficialdni bigint, texto varchar(250), hora_test time, fecha_test date)
AS
$BODY$
SELECT
	*
FROM testimonio t
WHERE t.idcaso = testimoniosCaso.inidcaso;
$BODY$
LANGUAGE sql;

--10a Si quieren todos los testimonios de cada caso
CREATE OR REPLACE FUNCTION testimoniosCategoria(inidcat integer)
RETURNS TABLE(idtest integer, personadni bigint, idcaso integer, oficialdni bigint, texto varchar(250), hora_test time, fecha_test date)
AS
$BODY$
SELECT
	t.*
FROM testimonio t
INNER JOIN caso c
on t.idcaso = c.idcaso
WHERE c.id_categoria = testimoniosCategoria.inidcat
ORDER BY t.idcaso;
$BODY$
LANGUAGE sql;

--10b Si quieren la cantidad de testimonios de cada caso
CREATE OR REPLACE FUNCTION testimoniosCategoriaCant(inidcat integer)
RETURNS TABLE(idcaso integer, cantidad_de_casos bigint)
AS
$BODY$
SELECT
	t.idcaso,
	count(t.idtest) as cantidad_de_casos
FROM testimonio t
INNER JOIN caso c
on t.idcaso = c.idcaso
WHERE c.id_categoria = testimoniosCategoriaCant.inidcat
GROUP BY t.idcaso
ORDER BY count(t.idtest) DESC;
$BODY$
LANGUAGE sql;

