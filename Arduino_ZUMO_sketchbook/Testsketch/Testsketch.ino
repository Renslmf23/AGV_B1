#include <ZumoShield.h>
#include <Wire.h>

ZumoMotors motors;

int direction = 0;
int speed = 100;

String inputString = "";         // a String to hold incoming data
bool stringComplete = false;  // whether the string is complete


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
}

void loop() {
  // put your main code here, to run repeatedly:
  motors.setLeftSpeed(speed - direction);
  motors.setRightSpeed(speed + direction);
}

void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      timeAtCommand = millis();
      char identifier = inputString.charAt(0); //read the id from the command
      inputString.remove(0, 1); //strip the command letter
      if (identifier == 'D') { //if the command is a directional command
        direction = inputString.toInt() * 5;
      } else if (identifier == 'E') { //if the command is a end of field command
        //do stuff
      } else if (identifier == 'T') { //if the camera detected a tree
        //do stuff
      }
      inputString = "";
    } else {
      // add it to the inputString:
      inputString += inChar;
    }
  }
}
}
