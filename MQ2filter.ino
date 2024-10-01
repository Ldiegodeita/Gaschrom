float r1 = 70000;
float r2 = 1000;
int numSamples = 10;  // Número de muestras para el filtro de media móvil
float readings[10];   // Array para almacenar las lecturas del sensor
int readIndex = 0;    // Índice actual de lectura
float total = 0;      // Suma total de las lecturas
float average = 0;    // Promedio de las lecturas
int sampleCount = 0;  // Contador de muestras reales

void setup() {
  Serial.begin(9600);    // Inicializa la comunicación serie a 9600 baudios.
  // Inicializa las lecturas en 0
  for (int i = 0; i < numSamples; i++) {
    readings[i] = 0;
  }
}

void loop() {
  // Lee el valor analógico del sensor en el pin A0 y lo convierte a voltaje
  float v = (analogRead(0) * 5.0) / 1024.0;
  
  // Calcula el valor ajustado con el divisor de resistencias
  float vmq2 = (v / (r2 / (r1 + r2))) * 10 + 1;
  
  // Si el valor es menor que 2, se ajusta a 0 para evitar valores insignificantes
  if (vmq2 < 2) {
    vmq2 = 0.00;
  }

  // --- Filtro de media móvil ---
  total = total - readings[readIndex];  // Restamos la lectura más antigua
  readings[readIndex] = vmq2;           // Reemplazamos con la nueva lectura
  total = total + readings[readIndex];  // Sumamos la nueva lectura
  readIndex = (readIndex + 1) % numSamples;  // Mover el índice circularmente
  
  // Solo calcular el promedio si tenemos al menos 10 muestras válidas
  if (sampleCount < numSamples) {
    sampleCount++;
    average = total / sampleCount;  // Usar solo las muestras disponibles
  } else {
    average = total / numSamples;   // Una vez llenas las 10 muestras, usar la media completa
  }
  
  // Enviar la lectura suavizada (media móvil) a través del puerto serial
  Serial.print("SENSOR,");
  Serial.println(average);

  // Pausa de 1 segundo antes de la siguiente lectura
  delay(1000);
}
