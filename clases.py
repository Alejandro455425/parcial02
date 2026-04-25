import os
import pandas as pd
from scipy.io import loadmat, whosmat
import matplotlib.pyplot as plt
import numpy as np

def pedir_entero(mensaje, minimo=None, maximo=None):
    """Pide un entero al usuario hasta que sea valido."""
    while True:
        try:
            valor = int(input(mensaje))
            if minimo is not None and valor < minimo:
                print(f"  >> El valor debe ser >= {minimo}.")
                continue
            if maximo is not None and valor > maximo:
                print(f"  >> El valor debe ser <= {maximo}.")
                continue
            return valor
        except ValueError:
            print("  >> Entrada invalida, ingrese un numero entero.")


def pedir_flotante(mensaje):
    while True:
        try:
            return float(input(mensaje))
        except ValueError:
            print("  >> Entrada invalida, ingrese un numero.")

def pedir_texto(mensaje):
    while True:
        texto = input(mensaje).strip()
        if texto:
            return texto
        print("  >> No puede estar vacío.")


def pedir_opcion(mensaje, opciones):
    """
    Función auxiliar para validar que el usuario elija 
    una de las llaves disponibles.
    """
    while True:
        res = input(mensaje)
        if res in opciones:
            return res
        print(f"Llave no válida. Opciones: {opciones}")

def cargar(ruta):
    """
    Carga un archivo según su extensión (.mat o .csv).
    """
    if not os.path.isfile(ruta):
        print(f"  >> Archivo no encontrado en la ruta: {ruta}")
        return None

    # Procesamiento de archivos MATLAB
    if ruta.lower().endswith(".mat"):
        try:
            # Obtener metadatos sin cargar todo el archivo aún
            info_variables = whosmat(ruta)
            print("  >> Variables detectadas (whosmat):")
            for v in info_variables:
                print(f"     - Nombre: {v[0]}, Forma: {v[1]}, Tipo: {v[2]}")
            
            # Cargar el diccionario completo
            datos_mat = loadmat(ruta)
            
            # Filtrar las llaves internas  (__header__, etc.)
            llaves = [k for k in datos_mat.keys() if not k.startswith("__")]
            
            # Selección de la llave por el usuario
            llave_elegida = pedir_opcion("  >> Ingrese el nombre de la llave a usar: ", llaves)
            
            matriz = datos_mat[llave_elegida]
            print(f"  >> Matriz '{llave_elegida}' cargada exitosamente.")
            return matriz
            
        except Exception as e:
            print(f"  >> Error al cargar .mat: {e}")
            return None

    # Procesamiento de archivos CSV
    elif ruta.lower().endswith(".csv"):
        try:
            df = pd.read_csv(ruta)
            print(f"  >> Archivo CSV cargado exitosamente. Columnas: {list(df.columns)}")
            return df
        except Exception as e:
            print(f"  >> Error al cargar .csv: {e}")
            return None

    else:
        print("  >> Extensión no soportada. Use .mat o .csv.")
        return None
    

class Persona:
    def __init__(self, nombre="", cc=0, edad=0, genero=""):
        self.__nombre = nombre
        self.__cc = cc
        self.__edad = edad
        self.__genero = genero
        # Cada paciente puede tener varios archivos cargados
        self.__archivos_csv = {}   # nombre -> ArchivoSIATA
        self.__archivos_mat = {}   # nombre -> ArchivoEEG

    # --- setters ---
    def asignar_nombre(self, t):  self.__nombre = t
    def asignar_cc(self, t):      self.__cc = t
    def asignar_edad(self, e):    self.__edad = e
    def asignar_genero(self, g):  self.__genero = g

    # --- getters ---
    def ver_nombre(self):  return self.__nombre
    def ver_cc(self):      return self.__cc
    def ver_edad(self):    return self.__edad
    def ver_genero(self):  return self.__genero

    # --- archivos ---
    def agregar_csv(self, alias, archivo):
        self.__archivos_csv[alias] = archivo

    def agregar_mat(self, alias, archivo):
        self.__archivos_mat[alias] = archivo

    def ver_csv(self, alias):
        return self.__archivos_csv.get(alias, None)

    def ver_mat(self, alias):
        return self.__archivos_mat.get(alias, None)

    def listar_csv(self):
        return list(self.__archivos_csv.keys())

    def listar_mat(self):
        return list(self.__archivos_mat.keys())

    def __str__(self):
        return (f"Paciente {self.__nombre} (CC {self.__cc}, "
                f"{self.__edad} años, {self.__genero}) | "
                f"CSV: {self.listar_csv()} | MAT: {self.listar_mat()}")
    
