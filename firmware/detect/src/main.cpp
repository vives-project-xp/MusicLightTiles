#include <Arduino.h>


  const int buttonPin = 16;
  int buttonState = 0;
  const int switchPin = 17;
  int switchState = 0;

void setup() {
  // put your setup code here, to run once:
  
   pinMode(buttonPin,INPUT);
   pinMode(switchPin,INPUT);
   Serial.begin(9600);
   
  
}

void loop() {
  // put your main code here, to run repeatedly:
  buttonState = digitalRead(buttonPin);
  switchState = digitalRead(switchPin);

  if(buttonState == 1){
      //Turn led on
      

      //sound on



       //digitalWrite(ledpin,HIGH);
       digitalWrite(Serial.print("haha It works\n"),HIGH);
       
  }


  else if (buttonState == 0){
      // Turn LED off

      //digitalWrite(led,LOW);
      digitalWrite(Serial.print("RIP the leds\n"),LOW);
      
  }

  if(switchState == 1){
       // Turn on power
       //digitalWrite(voeding,HIGH)
       digitalWrite(Serial.print("Voeding aan\n"),HIGH);

  }

  else if(switchState == 0){

    //Turn off power
    //digitalWrite(voeding,LOW);
    digitalWrite(Serial.print("Voeding uit"),LOW);



  }

    delay(2000);

}






