#define trigPin 4
#define echoPin 2

volatile unsigned long LastPulseTime;
int duration;

void setup()
{
  Serial.begin(9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  attachInterrupt(0, Echo_ISR, CHANGE);
}

void loop()
{
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  Serial.print("Sensor");
  Serial.print(LastPulseTime);
  Serial.print('\t');
  Serial.print((LastPulseTime / 2) * 0.0343);                     
  Serial.println("cm");

  delay(1000);
}

void Echo_ISR()
{
  static unsigned long startTime;

  if (digitalRead(2))
  {
    startTime = micros();
  }
  else
  {
    LastPulseTime = micros() - startTime;
  }
}
