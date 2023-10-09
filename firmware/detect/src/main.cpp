#include <Arduino.h>


  const int buttonPin = 16;
  int buttonState=0;

void setup() {
  // put your setup code here, to run once:
  
   pinMode(buttonPin,INPUT);
   Serial.begin(9600);
  
}

void loop() {
  // put your main code here, to run repeatedly:
  buttonState= digitalRead(buttonPin);

  if(buttonState == 1){
      //Turn led on

       //digitalWrite(ledpin,HIGH);
       digitalWrite(Serial.print("haha It works\n"),HIGH);
       
  }


  else if (buttonState == 0){
      // Turn LED off

      //digitalWrite(led,LOW);
      digitalWrite(Serial.print("RIP the leds\n"),LOW);
      
  }

    delay(2000);

}






