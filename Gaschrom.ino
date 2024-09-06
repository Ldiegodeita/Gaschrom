float vp = 1.7;
float r1 = 70000;
float r2 = 1000;
float ts = 0;

void setup() {
  Serial.begin(9600);
  Serial.println("CLEARDATA");
  Serial.println("LABEL");
    Serial.println("RESETTIMER");
 Serial.println((int) (vp / (r2 / (r1 + r2))));
  delay(1000);

}

void loop() {
  float v = (analogRead (0) * 5) / 1024.0;
   float vmq2 = ((v / (r2 / (r1 + r2))*10)+1); // here you can calibrate the sensor
   if (vmq2 <2) {
  vmq2 = 0.00;
   }
  
Serial.print("DATA,TIME,TIMER,");
Serial.println(vmq2);
 
delay (1000);
}
