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
    
class ArchivoEEG:
    """
    Manipula los archivos .mat de electroencefalografia (EEG) 
      Frecuencia de muestreo: 1 kHz.
    """

    FS = 1000  # Hz

    def __init__(self, ruta):
        self.__ruta = ruta
        self.__contenido = loadmat(ruta)
        self.__llaves = [k for k in self.__contenido.keys()
                         if not k.startswith("__")]
        self.__senal = None         # matriz seleccionada (puede ser 3D)
        self.__llave_actual = None

    # ---------- exploracion ----------
    def whosmat(self):
        """Devuelve la lista de variables guardadas en el .mat."""
        return whosmat(self.__ruta)

    def llaves(self):
        return self.__llaves

    def asignar_senal(self, llave):
        if llave not in self.__contenido:
            print(f"  >> La llave '{llave}' no existe en el .mat.")
            return None
        self.__senal = np.asarray(self.__contenido[llave])
        self.__llave_actual = llave
        print(f"  >> Señal cargada. Forma: {self.__senal.shape}, "
              f"dimension: {self.__senal.ndim}")
        return self.__senal.shape

    def senal(self):
        return self.__senal

    def llave_actual(self):
        return self.__llave_actual

    # ---------- helpers ----------
    def _matriz_2d(self):
        """Devuelve una vista 2D (canales x muestras) de la señal."""
        if self.__senal is None:
            return None
        if self.__senal.ndim == 2:
            return self.__senal
        if self.__senal.ndim == 3:
            # Convencion: (canales, muestras, epocas) -> promedio de epocas.
            # Si la convencion del archivo fuera distinta, igual queda 2D.
            return self.__senal.mean(axis=2)
        # Para mas dimensiones colapsamos a 2D
        return self.__senal.reshape(self.__senal.shape[0], -1)

    def numero_canales(self):
        m = self._matriz_2d()
        return 0 if m is None else m.shape[0]

    def numero_puntos(self):
        m = self._matriz_2d()
        return 0 if m is None else m.shape[1]

    # ---------- operacion (a): suma de 3 canales ----------
    def sumar_3_canales(self, c1, c2, c3, pmin, pmax):
        """Devuelve (segmento 3xN, suma 1xN) entre pmin y pmax."""
        m = self._matriz_2d()
        if m is None:
            print("  >> No hay señal cargada.")
            return None, None
        n_ch, n_pt = m.shape
        for c in (c1, c2, c3):
            if c < 0 or c >= n_ch:
                print(f"  >> Canal {c} fuera de rango (0..{n_ch-1}).")
                return None, None
        if pmin < 0 or pmax > n_pt or pmin >= pmax:
            print(f"  >> Rango de puntos invalido (0..{n_pt}).")
            return None, None

        seg = m[[c1, c2, c3], pmin:pmax]
        return seg, seg.sum(axis=0)

    def graficar_canales_y_suma(self, c1, c2, c3, pmin, pmax,
                                graficadora=None, guardar=True,
                                formato="png"):
        seg, suma = self.sumar_3_canales(c1, c2, c3, pmin, pmax)
        if seg is None:
            return
        t = np.arange(pmin, pmax) / self.FS  # segundos

        fig, axs = plt.subplots(2, 1, figsize=(11, 7))
        offsets = [0, 200, 400]   # microvoltios para separar visualmente
        for i, c in enumerate([c1, c2, c3]):
            axs[0].plot(t, seg[i] + offsets[i], label=f"Canal {c}")
        axs[0].set_title(f"Canales seleccionados: {c1}, {c2}, {c3}")
        axs[0].set_xlabel("Tiempo (s)")
        axs[0].set_ylabel("Voltaje (uV)")
        axs[0].legend(loc="upper right")
        axs[0].grid(True, alpha=0.3)

        axs[1].plot(t, suma, color="crimson")
        axs[1].set_title(f"Suma de los canales {c1} + {c2} + {c3}")
        axs[1].set_xlabel("Tiempo (s)")
        axs[1].set_ylabel("Voltaje (uV)")
        axs[1].grid(True, alpha=0.3)

        fig.tight_layout()
        if guardar and graficadora is not None:
            nombre = (f"eeg_suma_canales_{c1}_{c2}_{c3}_"
                      f"{pmin}-{pmax}.{formato}")
            graficadora.guardar(fig, nombre)
        plt.show()

    # ---------- operacion (b): promedio y desviacion en 3D ----------
    def estadisticos_3d(self, eje, graficadora=None, guardar=True):
        """
        Sobre la matriz SIN modificar (3D), calcula promedio y desviacion
        a lo largo del eje pedido y los muestra con stem en dos subplots.
        """
        if self.__senal is None:
            print("  >> No hay señal cargada.")
            return
        if self.__senal.ndim != 3:
            print(f"  >> La señal no es 3D (es {self.__senal.ndim}D). "
                  "El taller pide trabajar sobre la matriz 3D original.")
            return
        if eje not in (0, 1, 2):
            print("  >> El eje debe ser 0, 1 o 2.")
            return

        prom = np.mean(self.__senal, axis=eje)
        desv = np.std(self.__senal, axis=eje)

        # Reducimos a 1D promediando las dimensiones que sobren para
        # poder graficar con stem.
        prom_1d = prom
        desv_1d = desv
        while prom_1d.ndim > 1:
            prom_1d = prom_1d.mean(axis=-1)
            desv_1d = desv_1d.mean(axis=-1)

        fig, axs = plt.subplots(2, 1, figsize=(11, 7))
        axs[0].stem(prom_1d)
        axs[0].set_title(f"Promedio a lo largo del eje {eje}")
        axs[0].set_xlabel("Indice")
        axs[0].set_ylabel("Promedio (uV)")
        axs[0].grid(True, alpha=0.3)

        axs[1].stem(desv_1d)
        axs[1].set_title(f"Desviacion estandar a lo largo del eje {eje}")
        axs[1].set_xlabel("Indice")
        axs[1].set_ylabel("Desv. estandar (uV)")
        axs[1].grid(True, alpha=0.3)

        fig.tight_layout()
        if guardar and graficadora is not None:
            graficadora.guardar(fig, f"eeg_promedio_desv_eje{eje}.png")
        plt.show()

