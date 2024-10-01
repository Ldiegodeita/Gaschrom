import serial
import serial.tools.list_ports
import time
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv

class DIYChromatographApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DIY Chromatograph")
        
        self.serial_connection = None  # Para la conexión del puerto serial
        self.data = []  # Datos del sensor
        self.filtered_data = []  # Datos filtrados
        self.filter_window = 6  # Tamaño del filtro de media móvil por defecto
        self.csv_file = None
        self.csv_writer = None
        self.start_time = None
        self.recording = False
        self.marker_position = None  # Para almacenar la posición del marcador

        # Crear elementos de la interfaz
        self.create_ui()
        
        # Inicializar la gráfica
        self.setup_plot()

    def create_ui(self):
        # Frame superior para el título
        title_frame = tk.Frame(self.root)
        title_frame.pack(pady=10)
        tk.Label(title_frame, text="DIY Chromatograph", font=("Arial", 16, "bold")).pack()

        # Frame para la gráfica
        graph_frame = tk.Frame(self.root)
        graph_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Frame para la gráfica
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Frame para los controles inferiores
        controls_frame = tk.Frame(self.root)
        controls_frame.pack(pady=10)

        # Cuadro de texto para "Filter Time"
        tk.Label(controls_frame, text="Filter Time:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_time_entry = tk.Entry(controls_frame, width=10)
        self.filter_time_entry.insert(0, "6")  # Valor por defecto del filtro
        self.filter_time_entry.grid(row=1, column=0, padx=5)

        # Etiqueta para mostrar el tiempo transcurrido
        self.time_label = tk.Label(controls_frame, text="Time: 0 s")
        self.time_label.grid(row=2, column=0, padx=5, pady=5)

        # Etiqueta para mostrar el valor actual del sensor
        self.sensor_value_label = tk.Label(controls_frame, text="Sensor Value: 0")
        self.sensor_value_label.grid(row=3, column=0, padx=5, pady=5)

        # Botones en la parte inferior derecha
        button_frame = tk.Frame(controls_frame)
        button_frame.grid(row=0, column=1, rowspan=4, padx=10, pady=5)

        self.start_button = tk.Button(button_frame, text="Start Chrom", command=self.start_chrom)
        self.start_button.grid(row=0, column=0, pady=5)

        self.connect_button = tk.Button(button_frame, text="Connect", command=self.connect_to_arduino)
        self.connect_button.grid(row=1, column=0, pady=5)

        self.close_button = tk.Button(button_frame, text="Close", command=self.close_connection)
        self.close_button.grid(row=1, column=1, pady=5, padx=5)

    def setup_plot(self):
        """ Configura el gráfico en tiempo real """
        self.ax.set_title("MQ-sensor")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Sensor Value")
        self.ani = animation.FuncAnimation(self.fig, self.update_plot, interval=1000)

    def update_plot(self, frame):
        """ Actualiza el gráfico con los datos nuevos """
        if len(self.data) > 0:
            times = [i for i in range(len(self.data))]
            self.ax.clear()
            self.ax.plot(times, self.data, label="MQ-Sensor (Raw)")
            self.ax.plot(times, self.filtered_data, label="Filtered Sensor Data")
            
            if self.recording and self.marker_position is not None:
                # Añadir un marcador dinámico en la posición del marcador (que aumenta con el tiempo)
                self.ax.axvline(x=self.marker_position, color='r', linestyle='--', label="Start Chrom Marker")
            
            self.ax.set_title("MQ-sensor")
            self.ax.set_xlabel("Time (s)")
            self.ax.set_ylabel("Sensor Value")
            self.ax.legend()
            self.canvas.draw()

    def apply_moving_average_filter(self, new_value):
        """ Aplica un filtro de media móvil a los datos """
        self.data.append(new_value)
        if len(self.data) < self.filter_window:
            # Si hay menos valores que la ventana de filtro, usar los valores disponibles
            self.filtered_data.append(sum(self.data) / len(self.data))
        else:
            # Aplicar filtro de media móvil
            window_data = self.data[-self.filter_window:]
            self.filtered_data.append(sum(window_data) / self.filter_window)

    def start_chrom(self):
        """ Inicia la adquisición de datos y registro en CSV o reinicia todo si ya está corriendo """
        if not self.recording:
            # Desactivar el cuadro de entrada de filtro
            self.filter_time_entry.config(state='disabled')

            # Crear un archivo CSV
            self.csv_file = open('chromatograph_data.csv', 'w', newline='')
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow(['Time', 'MQ-Sensor', 'Filtered Sensor'])

            # Marcar el inicio del cronómetro
            self.start_time = time.time()
            self.recording = True
            self.marker_position = len(self.data)  # Establecer la posición del marcador en el punto actual
            self.start_button.config(text="Reset")  # Cambiar el botón a "Reset"
            print("Comenzando la adquisición y registro en CSV.")
        else:
            # Reiniciar todo si ya está en modo "Reset"
            self.reset_data()

    def reset_data(self):
        """ Reinicia los datos y el archivo CSV """
        self.data.clear()
        self.filtered_data.clear()
        self.marker_position = None
        self.start_time = None
        self.recording = False

        # Cerrar el archivo CSV actual y crear uno nuevo
        if self.csv_file:
            self.csv_file.close()
            print("Archivo CSV cerrado.")

        # Habilitar de nuevo el cuadro de entrada del filtro
        self.filter_time_entry.config(state='normal')
        self.start_button.config(text="Start Chrom")  # Volver a cambiar el botón a "Start Chrom"
        self.time_label.config(text="Time: 0 s")
        self.sensor_value_label.config(text="Sensor Value: 0")
        print("Datos reiniciados.")

    def connect_to_arduino(self):
        """ Conecta automáticamente al puerto Arduino y comienza la lectura de datos """
        if not self.serial_connection:
            arduino_port = self.find_arduino()
            if arduino_port:
                try:
                    self.serial_connection = serial.Serial(arduino_port, 9600, timeout=1)
                    time.sleep(2)
                    print(f"Conectado a Arduino en {arduino_port}")

                    # Obtener el filtro desde el cuadro de texto
                    try:
                        self.filter_window = int(self.filter_time_entry.get())
                    except ValueError:
                        self.filter_window = 6
                        self.filter_time_entry.delete(0, tk.END)
                        self.filter_time_entry.insert(0, "6")

                    # Comenzar a leer los datos
                    self.read_serial_data()
                except serial.SerialException as e:
                    messagebox.showerror("Error", f"No se pudo conectar a {arduino_port}: {e}")
            else:
                messagebox.showerror("Error", "No se encontró un Arduino conectado.")
    
    def read_serial_data(self):
        """ Lee los datos del sensor desde el puerto serial """
        def read_loop():
            while self.serial_connection and self.serial_connection.in_waiting:
                try:
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    if "SENSOR" in line:
                        sensor_value = float(line.split(",")[1])
                        self.apply_moving_average_filter(sensor_value)
                        
                        if self.recording and self.start_time is not None:
                            elapsed_time = time.time() - self.start_time
                            self.time_label.config(text=f"Time: {int(elapsed_time)} s")
                            self.sensor_value_label.config(text=f"Sensor Value: {sensor_value}")

                            # Escribir datos en el archivo CSV
                            self.csv_writer.writerow([elapsed_time, sensor_value, self.filtered_data[-1]])
                except Exception as e:
                    print(f"Error al leer datos: {e}")
                    break

            # Vuelve a llamar esta función después de 100 ms para leer datos continuamente
            if self.serial_connection:
                self.root.after(100, read_loop)

        read_loop()

    def close_connection(self):
        """ Cierra la conexión serial y el archivo CSV """
        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None
            print("Conexión serial cerrada.")

        if self.csv_file:
            self.csv_file.close()
            print("Archivo CSV cerrado.")
            self.csv_file = None
            self.recording = False

    def find_arduino(self):
        """ Busca el puerto al que está conectado el Arduino """
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if 'Arduino' in port.description or 'CH340' in port.description:
                return port.device
        return None

# Crear la ventana principal de Tkinter
root = tk.Tk()
app = DIYChromatographApp(root)
root.mainloop()
