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
    
class Graficadora:
    """Encapsula la creacion y guardado de figuras de matplotlib."""

    CARPETA_SALIDA = "graficos"

    def __init__(self):
        if not os.path.isdir(self.CARPETA_SALIDA):
            os.makedirs(self.CARPETA_SALIDA, exist_ok=True)

    def guardar(self, fig, nombre):
        """Guarda la figura en /graficos/<nombre>. Devuelve la ruta."""
        ruta = os.path.join(self.CARPETA_SALIDA, nombre)
        fig.savefig(ruta, bbox_inches="tight")
        print(f"  >> Grafico guardado en: {ruta}")
        return ruta
    
class ArchivoSIATA:
    """
    Manipula los archivos CSV del SIATA. Encapsula el DataFrame de pandas
    y desarrollo (info, describe, graficos,
    apply, map, suma/resta de columnas, set_index y resample).
    """

    def __init__(self, ruta):
        self.__ruta = ruta
        self.__df = pd.read_csv(ruta)
        self.__indice_es_fecha = False

    # ---------- exploracion ----------
    def info(self):
        print(f"\n--- info() de {os.path.basename(self.__ruta)} ---")
        self.__df.info()

    def describe(self):
        print(f"\n--- describe() de {os.path.basename(self.__ruta)} ---")
        print(self.__df.describe(include="all"))

    def columnas(self):
        return list(self.__df.columns)

    def head(self, n=5):
        return self.__df.head(n)

    def datos(self):
        return self.__df

    def es_fecha_indexado(self):
        return self.__indice_es_fecha

    # ---------- graficos individuales ----------
    def graficar(self, columna, tipo, graficadora=None, guardar=False):
        """tipo: 'plot' | 'boxplot' | 'histograma'"""
        if columna not in self.__df.columns:
            print(f"  >> La columna '{columna}' no existe.")
            return

        fig, ax = plt.subplots(figsize=(9, 5))
        if tipo == "plot":
            self.__df[columna].plot(ax=ax)
            ax.set_title(f"Plot de {columna}")
            ax.set_ylabel(columna)
        elif tipo == "boxplot":
            self.__df.boxplot(column=[columna], ax=ax)
            ax.set_title(f"Boxplot de {columna}")
        elif tipo == "histograma":
            self.__df[columna].plot(kind="hist", bins=30, ax=ax)
            ax.set_title(f"Histograma de {columna}")
            ax.set_xlabel(columna)
        else:
            print("  >> Tipo de grafico invalido.")
            plt.close(fig)
            return

        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        if guardar and graficadora is not None:
            graficadora.guardar(fig, f"siata_{tipo}_{columna}.png")
        plt.show()

    def graficar_subplots(self, columna, graficadora=None, guardar=False):
        """Muestra plot, boxplot e histograma de la misma columna en subplots."""
        if columna not in self.__df.columns:
            print(f"  >> La columna '{columna}' no existe.")
            return

        fig, axs = plt.subplots(3, 1, figsize=(9, 11))
        self.__df[columna].plot(ax=axs[0])
        axs[0].set_title(f"Plot de {columna}")
        axs[0].grid(True, alpha=0.3)

        self.__df.boxplot(column=[columna], ax=axs[1])
        axs[1].set_title(f"Boxplot de {columna}")

        self.__df[columna].plot(kind="hist", bins=30, ax=axs[2])
        axs[2].set_title(f"Histograma de {columna}")
        axs[2].grid(True, alpha=0.3)

        fig.suptitle(f"Resumen grafico de la columna '{columna}'",
                     fontsize=13, y=1.02)
        fig.tight_layout()
        if guardar and graficadora is not None:
            graficadora.guardar(fig, f"siata_subplots_{columna}.png")
        plt.show()

    # ---------- operaciones apply / map / suma-resta ----------
    def operacion_apply(self, columna):
        """
        APPLY #1: eleva al cuadrado los valores numericos.
        Devuelve una nueva Serie sin modificar el DataFrame.
        """
        if columna not in self.__df.columns:
            print(f"  >> La columna '{columna}' no existe.")
            return None
        return self.__df[columna].apply(
            lambda x: x ** 2 if pd.notna(x) and isinstance(x, (int, float)) else x
        )

    def operacion_map(self, columna):
        """
        MAP #1: clasifica cada valor numerico en 'bajo', 'medio' o 'alto'
        usando los terciles de la columna.
        """
        if columna not in self.__df.columns:
            print(f"  >> La columna '{columna}' no existe.")
            return None
        serie = pd.to_numeric(self.__df[columna], errors="coerce")
        if serie.dropna().empty:
            print("  >> La columna no tiene valores numericos.")
            return None
        q1 = serie.quantile(0.33)
        q2 = serie.quantile(0.66)

        def clasificar(x):
            if pd.isna(x):
                return "sin dato"
            if x <= q1:
                return "bajo"
            if x <= q2:
                return "medio"
            return "alto"

        return serie.map(clasificar)

    def operacion_columnas(self, col1, col2, operacion="sumar"):
        """Suma o resta dos columnas numericas elegidas por el usuario."""
        for c in (col1, col2):
            if c not in self.__df.columns:
                print(f"  >> La columna '{c}' no existe.")
                return None
        s1 = pd.to_numeric(self.__df[col1], errors="coerce")
        s2 = pd.to_numeric(self.__df[col2], errors="coerce")
        return s1 + s2 if operacion == "sumar" else s1 - s2

    # ---------- fechas y resample ----------
    def configurar_indice_fecha(self, columna_fecha):
        """Convierte la columna a datetime y la pone como indice (set_index)."""
        if columna_fecha not in self.__df.columns:
            print(f"  >> La columna '{columna_fecha}' no existe.")
            return False
        self.__df[columna_fecha] = pd.to_datetime(
            self.__df[columna_fecha], errors="coerce"
        )
        self.__df = self.__df.dropna(subset=[columna_fecha])
        self.__df = self.__df.set_index(columna_fecha).sort_index()
        self.__indice_es_fecha = True
        print(f"  >> Indice configurado por fecha ({columna_fecha}).")
        return True

    def remuestrear_y_graficar(self, columna, frecuencia,
                               graficadora=None, guardar=True):
        """
        frecuencia: 'D' (dias), 'M' (meses), 'Q' (trimestres).
        Promedia los valores numericos de la columna y los grafica.
        """
        if not self.__indice_es_fecha:
            print("  >> Primero configure el indice de fecha (set_index).")
            return
        if columna not in self.__df.columns:
            print(f"  >> La columna '{columna}' no existe.")
            return

        serie = pd.to_numeric(self.__df[columna], errors="coerce")
        remuestreada = serie.resample(frecuencia).mean()
        etiqueta = {"D": "Diario", "M": "Mensual", "Q": "Trimestral"}.get(
            frecuencia, frecuencia
        )

        fig, ax = plt.subplots(figsize=(10, 5))
        remuestreada.plot(ax=ax, marker="o")
        ax.set_title(f"{columna} remuestreada ({etiqueta})")
        ax.set_xlabel("Fecha")
        ax.set_ylabel(columna)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()

        if guardar and graficadora is not None:
            graficadora.guardar(
                fig, f"siata_resample_{etiqueta}_{columna}.png"
            )
        plt.show()
    
