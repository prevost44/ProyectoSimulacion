import os
import joblib
import pandas as pd
from django.conf import settings
from django.shortcuts import render

columnasModelo = [
    'Age','Pos','G','MP','FG','FGA','FG%','3P','3PA','3P%','2P','2PA','2P%',
    'eFG%','FT','FTA','FT%','ORB','DRB','TRB','AST','STL','BLK','TOV','PF'
]


decadas = ["80s", "90s", "00s", "10s", "20s"]

def completarCamposModelo(entrada):
    entrada["3PA"] = max(entrada["3PA"], entrada["3P"])
    entrada["2PA"] = max(entrada["2PA"], entrada["2P"])
    entrada["FTA"] = max(entrada["FTA"], entrada["FT"])
    entrada["FG"] = entrada["2P"] + entrada["3P"]
    entrada["FGA"] = entrada["2PA"] + entrada["3PA"]


    entrada["FG%"] = round((entrada["FG"] / entrada["FGA"]) * 100 if entrada["FGA"] > 0 else 0, 1)
    entrada["2P%"] = round((entrada["2P"] / entrada["2PA"]) * 100 if entrada["2PA"] > 0 else 0, 1)
    entrada["3P%"] = round((entrada["3P"] / entrada["3PA"]) * 100 if entrada["3PA"] > 0 else 0, 1)
    entrada["FT%"] = round((entrada["FT"] / entrada["FTA"]) * 100 if entrada["FTA"] > 0 else 0, 1)
    entrada["TRB"] = entrada["ORB"] + entrada["DRB"]
    entrada["eFG%"] = round(((entrada["2P"] + 0.5 * entrada["3P"]) / entrada["FGA"]) * 100 if entrada["FGA"] > 0 else 0, 1)
    return entrada


def cargarYPredecir(nombreModelo, datosEntrada):
    rutaModelo = os.path.join(settings.BASE_DIR, "modelosPrediccion", nombreModelo)
    if not os.path.exists(rutaModelo):
        raise FileNotFoundError(f"Modelo no encontrado: {rutaModelo}")
    modelo = joblib.load(rutaModelo)
    return modelo.predict(datosEntrada)[0]


def home(request):
    edades = range(18, 41)
    juegos = range(60, 83)
    campos = ["MP","2P","2PA","3P","3PA","FT","FTA","ORB","DRB","AST","STL","BLK","TOV","PF"]

    return render(request, "predictions/index.html", {
        "edades": edades,
        "juegos": juegos,
        "campos": campos
    })


def predecir(request):
    if request.method == "POST":
        try:
            #Obtener valores 
            edad = int(request.POST.get("Age"))
            posicion = int(request.POST.get("Pos"))
            juegos = int(request.POST.get("G"))

            campos = ["MP","2P","2PA","3P","3PA","FT","FTA","ORB","DRB","AST","STL","BLK","TOV","PF"]
            entrada = {"Age": edad, "Pos": posicion, "G": juegos}
            for campo in campos:
                valor = request.POST.get(campo)
                if valor is None or valor.strip() == "":
                    raise ValueError(f"Falta el valor para {campo}")
                
                valorNum = float(valor)
                if valorNum <= 0:
                    raise ValueError(f"El valor de '{campo}' debe ser mayor que 0.")
                
                entrada[campo] = valorNum


            #Validaciones
            if entrada["2P"] > entrada["2PA"]:
                raise ValueError("Los tiros de 2P encestados no pueden ser mayores que los intentados.")
            if entrada["3P"] > entrada["3PA"]:
                raise ValueError("Los tiros de 3P encestados no pueden ser mayores que los intentados.")
            if entrada["FT"] > entrada["FTA"]:
                raise ValueError("Los tiros libres encestados no pueden ser mayores que los intentados.")
            if entrada["MP"] < 10 or entrada["MP"] > 48:
                raise ValueError("Los minutos promedio deben estar entre 10 y 48.")
            if entrada["PF"] < 0.1 or entrada["PF"] > 6:
                raise ValueError("Las faltas personales deben estar entre 0.1 y 6.")

            #Ajustar valores obligatorios
            entrada["2PA"] = max(entrada["2PA"], entrada["2P"])
            entrada["3PA"] = max(entrada["3PA"], entrada["3P"])
            entrada["FTA"] = max(entrada["FTA"], entrada["FT"])

            #Calcular campos backend
            entradaCompleta = completarCamposModelo(entrada.copy())
            datosEntrada = pd.DataFrame([entradaCompleta])[columnasModelo]

            #Calcular puntos manuales
            puntosCalculados = round((entrada["FT"] * 1) + (entrada["2P"] * 2) + (entrada["3P"] * 3), 2)

            #Diccionario de porcentajes 
            porcentajes = {
                "FGP": entradaCompleta["FG%"],
                "P2P": entradaCompleta["2P%"],
                "P3P": entradaCompleta["3P%"],
                "FTP": entradaCompleta["FT%"],
                "eFGP": entradaCompleta["eFG%"]
            }

            #Generar predicciones
            resultados = {}
            for d in decadas:
                resultados[d] = {
                    "PuntosPorPartido": float(cargarYPredecir(f"modeloPPG{d}.pkl", datosEntrada)),
                    "AllStar": int(cargarYPredecir(f"modeloASG{d}.pkl", datosEntrada)),
                    "MVPTop5": int(cargarYPredecir(f"modeloMVP5_{d}.pkl", datosEntrada)),
                    "AllNBA": int(cargarYPredecir(f"modeloANT{d}.pkl", datosEntrada))
                }

            return render(request, "predictions/resultado.html", {
                "resultados": resultados,
                "statsUsuario": entrada,
                "puntosCalculados": puntosCalculados,
                "porcentajes": porcentajes
            })

        except Exception as e:
            edades = range(18, 41)
            juegos = range(60, 83)
            campos = ["MP","2P","2PA","3P","3PA","FT","FTA","ORB","DRB","AST","STL","BLK","TOV","PF"]
            return render(request, "predictions/index.html", {
                "edades": edades,
                "juegos": juegos,
                "campos": campos,
                "error": f"Error: {str(e)}"
            })

    return home(request)
