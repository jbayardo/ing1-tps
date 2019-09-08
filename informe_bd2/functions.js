// Numero promedio de crimenes cometidos por personas que ya han sido encontradas culpables de algun crimen.
var map1 = function() {
  if (this.culpable && this.culpable.length > 0) {
    emit(1, { qty: 1, sum: this.culpable.length })
  }
}

var reduce1 = function(key, values) {
  reducedVal = { sum: 0, qty: 0 };

  for (var idx = 0; idx < values.length; idx++) {
    reducedVal.sum += values[idx].sum;
    reducedVal.qty += values[idx].qty;
  }
  return reducedVal;
}

var finalize1 = function(key, reduced) {
  return reduced.sum / reduced.qty;
}

db.personas.mapReduce(
  map1,
  reduce1,
  {
    out: "promedio_crimenes_cometidos",
    finalize: finalize1
  }
);

// Personas involucradas como testigos en la mayor cantidad de casos.
var map2 = function() {
  var ncasos = 0;
  if (this.involucrado) {
    for (var idx = 0; idx < this.involucrado.length; idx++) {
        if (this.involucrado[idx].rol == 'testigo') {
        ncasos++;
      }
    }

  }
  if (ncasos > 0) { emit(ncasos, { personas : [this.dni] }); }
}

var reduce2 = function(key, values) {
  var res = { personas: [] }
  values.forEach(function(e){ res.personas.push.apply(res.personas,e.personas) })
  return res;
}

db.personas.mapReduce(map2, reduce2, { out: 'aux_2' });
db.createCollection('personas_involucradas_como_testigos');
db.personas_involucradas_como_testigos.insertMany(
  // Ordeno los resultados de mayor a menor, me quedo con el primero y me fijo las personas que contiene
  // Inserto cada persona como un objeto { dni: numero } a la coleccion final
  db.aux_2.find({}).sort({_id:-1})[0].value.personas.map(function(e){ return {dni: e}})
)
db.aux_2.drop() // Elimino coleccion auxiliar


//Casos en los que se han visto involucradas el mayor numero de personas.
var map3 = function() {
  emit(this.personas.length, { casos: [this.id] });
}

var reduce3 = function(key, values) {
  var res = { casos: [] }
  values.forEach(function(e){ res.casos.push.apply(res.casos,e.casos) })
  return res;
}

db.casos.mapReduce(map3, reduce3, { out: 'aux_3' });
db.createCollection('casos_con_mayor_numero_de_personas_involucradas');
db.casos_con_mayor_numero_de_personas_involucradas.insertMany(
  // Ordeno los resultados de mayor a menor, me quedo con el primero y me fijo los casos que contiene
  // Inserto cada caso como un objeto { caso: numero } a la coleccion final
  db.aux_3.find({}).sort({_id:-1})[0].value.casos.map(function(e){ return {caso: e}})
)

db.aux_3.drop() // Elimino coleccion auxiliar

// Cantidad de crimenes por localidad y por ano.
var map4 = function() {
  year = this.timestamp_suceso.getFullYear();
  d = {}
  d[year] = 1;
  emit(this.lugar_suceso.localidad, d);
}

var reduce4 = function(key, values) {
  d = {}
  for (i in values) {
    for (year in values[i]) {
      if (year in d) {
        d[year] = d[year]+1;
      } else {
        d[year] = 1;
      }
    }
  }
 return d;
}

db.casos.mapReduce(map4, reduce4, { out: 'crimenes_por_localidad_y_ano' });

// Mayor numero de crimenes cometido por alguna persona.
var map5 = function() {
  if (this.culpable) {
    emit(1, this.culpable.length);
  }
}

var reduce5 = function(key, values) {
  return values.reduce(function(pv, cv) { return (pv > cv) ? pv : cv ; }, 0);
}

db.personas.mapReduce(map5, reduce5, { out: 'mayor_numero_de_crimenes_cometidos_por_una_persona' });

// Cantidad total de evidencias por caso.
var map6 = function() {
  if (this.evidencia) {
    emit(this.id, this.evidencia.length);
  }
}

var reduce6 = function(key, values) {
  return values.reduce(function(pv, cv) { return pv + cv; }, 0);
}

db.casos.mapReduce(map6, reduce6, { out: 'cantidad_total_de_evidencias_por_caso' });

// Las 10 ciudades con mayor numero de crimenes.
var map7 = function() {
  emit(this.lugar_suceso.localidad, 1)
}

var reduce7 = function(key, values) {
  return values.reduce(function(pv, cv) { return pv + cv; }, 0);
}

db.casos.mapReduce(map7, reduce7, { out: 'ciudades_con_mayor_numero_de_crimenes' })

db.promedio_crimenes_cometidos.find()
db.personas_involucradas_como_testigos.find().sort( { value: -1 } );
db.casos_con_mayor_numero_de_personas_involucradas.find().sort( { value: -1 } );
db.crimenes_por_localidad_y_ano.find()
db.mayor_numero_de_crimenes_cometidos_por_una_persona.find()
db.cantidad_total_de_evidencias_por_caso.find()
db.ciudades_con_mayor_numero_de_crimenes.find().sort( { value: -1 } );
