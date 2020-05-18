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
      direction = inputString.toInt() * 30;

      inputString = "";
    } else {
    // add it to the inputString:
      inputString += inChar;
    }
    // if the incoming character is a newline, set a flag so the main loop can
    // do something about it:

  }

}
