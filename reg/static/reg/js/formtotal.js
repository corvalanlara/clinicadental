function nuevaLista() {
	var form = document.querySelector("#formtotal");
	var ul = document.createElement("ul");
	ul.id = "lista_prestaciones";
	var th = document.createElement("th");
	var row = form.insertRow(-1);
	row.appendChild(th);
	var td = row.insertCell(-1);
	td.appendChild(ul);

}

function nuevoCampo() {
	var form = document.querySelector("#formtotal");
	var td = form.querySelector('#id_prestaciones').parentNode;
	var etiqueta = document.createElement("label");
	etiqueta.innerText = "Pieza";
	td.appendChild(etiqueta);
	var inpieza = document.createElement("input");
	inpieza.type = "text";
	inpieza.id = "id_prestacion_pieza";
	inpieza.name = "prestacion_monto";
	inpieza.required = "";
	td.appendChild(inpieza);
	var signo = document.createElement("label");
	signo.innerText = "$";
	td.appendChild(signo);
	var inp2 = document.createElement("input");
	inp2.type = "text";
	inp2.id = "id_prestacion_monto";
	inp2.name = "prestacion_monto";
	inp2.required = "";
	td.appendChild(inp2);
	var boton = document.createElement("button");
	boton.value = "eliminar";
	boton.id = "botonmas";
	boton.type = "button";
	boton.innerText = "+";
	td.appendChild(boton);
}

function eliminarValorOculto() {
	var oculto = document.querySelector("#id_oculto");
	oculto.value= "";
}

function* itera(i) {
        while (true) {
                yield i++;
        }
}

function crearBoton(contexto, valor, pieza, monto, unico) {
        var boton = document.createElement('input');
        boton.type = 'button';
        //var span = document.createElement('span');
        //span.setAttribute('aria-hidden', 'true');
        //boton.appendChild(span);
        boton.value = "Eliminar";
        boton.setAttribute('class', 'btn btn-primary');
        //boton.setAttribute('aria-label', 'Close');
        boton.onclick = function() {
                var chao = document.querySelector('#'+ unico);
                chao.remove()
                var oculto = document.querySelector("#id_oculto");
                oculto.value = oculto.value.replace(
                        valor + ':' + pieza + ':' + monto + ';', '')
        };
        contexto.appendChild(boton);
}

eliminarValorOculto();
nuevoCampo();
nuevaLista();
const num = itera(0);
var boton = document.querySelector("#botonmas");
boton.addEventListener("click", function() {
	//Obtener datos
	var valor = document.querySelector("#id_prestaciones").innerText.split('\n').pop();
	var pieza = document.querySelector('#id_prestacion_pieza').value;
	var monto = document.querySelector("#id_prestacion_monto").value;
	var ul = document.querySelector("#lista_prestaciones");

	//Crear elementos
	var li = document.createElement("li");
	var unico = num.next().value;
	var identificacion = 'servicio' + unico;
	li.setAttribute('id', identificacion);
	var tn = document.createTextNode(valor + " " + pieza + ": " + monto);
	li.appendChild(tn);
	crearBoton(li, valor, pieza, monto, identificacion);
	ul.appendChild(li);

	//Ingresar a campo oculto
	var oculto = document.querySelector("#id_oculto");
	var valorymonto = valor + ":" + pieza + ":"  + monto;
	oculto.value += valorymonto + ";";
});

//Hacer span triggerable
//$(function(){
//	$(".selection").click(function() {
//		$("#select2-id_prestaciones-container").title($(this).title).trigger('change');
//	});
//});

//Evento que triggerea el ajax para precio de prestación
$(document).ready(function() {
 	$("#select2-id_prestaciones-container").on("DOMSubtreeModified", function() {
                        var nom = document.querySelector("#select2-id_prestaciones-container").title;
                        $.ajax({
				url: "ajax/chequear/",
                                data: {
                                        "nom": nom
                                },
                                dataType : 'json',
                                success: function(data) {
					if (data.precio) {
						document.querySelector("#id_prestacion_monto").value = data.precio.toString();
					}
                                },
                        });
                });
});


//var botonenvio = document.querySelector("#envioformtotal");
//botonenvio.addEventListener("click", eliminarValorOculto)
