int THRESHOLD = 10;
bool detected[4];
unsigned long value[4];
unsigned long sensor[4];
unsigned long detected_time = micros();

void setup() {
  Serial.begin(9600);
  
  for(int i=0;i<4;i++) {
    detected[i] = false;
    value[i] = 0;
  }
}

void loop() {
  if((micros() - detected_time) > 5000000) {
    for(int i=0;i<4;i++) {
      sensor[i] = analogRead(i);
      //Serial.print(sensor[i]);
      //Serial.print("@@@");
      if((sensor[i] > THRESHOLD) && (detected[i] == false)) {
        value[i] = micros();
        detected[i] = true;
      }
    }
    //Serial.println("");
    if(detected[0] && detected[1] && detected[2] && detected[3]) {
      for(int i=0;i<3;i++) {
        Serial.print(value[i]);
        Serial.print("@");
      }
      Serial.println(value[3]);
      for(int i=0;i<4;i++) {
        detected[i] = false;
      }
      detected_time = micros();
    }
    //else {
    //  for(int i=0;i<4;i++) {
    //    value[i] = 0;
    //    detected[i] = false;
    //  }
    //}
  }
}
