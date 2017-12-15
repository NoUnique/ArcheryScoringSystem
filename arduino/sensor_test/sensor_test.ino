void setup() {
  Serial.begin(9600);
}

void loop() {
  unsigned long sensor1, sensor2, sensor3, sensor4;
  int THRESHOLD = 10;
  sensor1 = analogRead(0);
  sensor2 = analogRead(1);
  sensor3 = analogRead(2);
  sensor4 = analogRead(3);
  
  if(sensor1 > THRESHOLD) {
    Serial.print("1:");
    Serial.println(sensor1, DEC);
    //Serial.println(micros(), DEC);//Print the analog value read via serial port
  }
  if(sensor2 > THRESHOLD) {
    Serial.print("2:");
    Serial.println(sensor2, DEC);
    //Serial.println(micros(), DEC);//Print the analog value read via serial port
  }
  if(sensor3 > THRESHOLD) {
    Serial.print("3:");
    Serial.println(sensor3, DEC);
    //Serial.println(micros(), DEC);//Print the analog value read via serial port
  }
  if(sensor4 > THRESHOLD) {
    Serial.print("4:");
    Serial.println(sensor4, DEC);
    //Serial.println(micros(), DEC);//Print the analog value read via serial port
  }
}
