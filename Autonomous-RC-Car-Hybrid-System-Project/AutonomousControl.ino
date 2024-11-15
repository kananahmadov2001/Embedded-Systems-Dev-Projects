/*
  This robot will drive around on its own and react to obstacles by backing up and turning to a new direction.
  The sketch was adapted from one of the activities in the SparkFun Guide to Arduino.
*/

// the right motor will be controlled by the motor A pins on the motor driver
const int AIN1 = 13;  //control pin 1 on the motor driver for the right motor
const int AIN2 = 12;  //control pin 2 on the motor driver for the right motor
const int PWMA = 11;  //speed control pin on the motor driver for the right motor

//the left motor will be controlled by the motor B pins on the motor driver
const int PWMB = 10;  //speed control pin on the motor driver for the left motor
const int BIN2 = 9;   //control pin 2 on the motor driver for the left motor
const int BIN1 = 8;   //control pin 1 on the motor driver for the left motor

//distance variables
const int trigPin = 2;
const int echoPin = 3;
const int buttonPin = 4;
const int ledPin = 5;
int switchPin = 7;  //switch to turn the robot on and off

int lastSteadyState = LOW;           // the previous steady state from the input pin
int lastFlickerableState = LOW;      // the previous flickerable state from the input pin
int currentState;                    // the current reading from the input pin
unsigned long lastDebounceTime = 0;  // the last time the output pin was toggled
unsigned long debounceDelay = 50;    // the debounce time; increase if the output flickers
unsigned long now;

byte incomingByte;
String infoString;
bool remote = true;
float distance = 0;  //variable to store the distance measured by the distance sensor
float rollingAvg;

//robot behaviour variables
int backupTime = 1000;  //amount of time that the robot will back up when it senses an object
int turnTime = 400;     //amount that the robot will turn once it has backed up
bool firstTime = false;
bool firstTimeInfo = false;
const int driveTimePerCm = 25;  //this is the number of milliseconds that it takes the robot to drive 1 cm
long lastDrive = 0;
byte incomingDriveDistance = 10;
int driveDistance;
long drivePeriod = driveTimePerCm * 1;
const int turnTimePerCm = 25;  //this is the number of milliseconds that it takes to turn the robot 1 degree

long lastEcho = 0;
const int echoDelay = 50;
long lastSendEcho = 0;
const int sendEchoDelay = 1000;

int turnState = 0;
unsigned long lastTurn = 0;
const long turnDelay = 500;
long turnDelayTotal = 0;
bool turning = false;

enum State {
  idle,
  receiving,
  move,
  moveFor
}

carState = receiving;

/********************************************************************************/
void setup() {
  pinMode(trigPin, OUTPUT);  //this pin will send ultrasonic pulses out from the distance sensor
  pinMode(echoPin, INPUT);   //this pin will sense when the pulses reflect back to the distance sensor
  pinMode(ledPin, OUTPUT);

  pinMode(switchPin, INPUT_PULLUP);  //set this as a pullup to sense whether the switch is flipped
  pinMode(buttonPin, INPUT_PULLUP);  //set this as a pullup to sense whether the button is pressed


  //set the motor control pins as outputs
  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(PWMA, OUTPUT);
  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);
  pinMode(PWMB, OUTPUT);

  digitalWrite(ledPin, LOW);

  Serial.begin(9600);                       //begin serial communication with the computer
  Serial.print("To infinity and beyond!");  //test the serial connection
}

/********************************************************************************/
void loop() {
  now = millis();
  if (now - lastSendEcho >= sendEchoDelay) {
    sendEcho();
    lastSendEcho += sendEchoDelay;
  }

  now = millis();
  if ((now - lastEcho) >= echoDelay) {
    distance = getDistance();
    lastEcho += echoDelay;
  }


  checkCarMode();
  if (!remote) {
    if (firstTime) firstTime = false;
    digitalWrite(ledPin, LOW);
    //DETECT THE DISTANCE READ BY THE DISTANCE SENSOR

    if (digitalRead(switchPin) == LOW) {  //if the on switch is flipped
      if (distance < 10 || turning) {

        turning = true;
        now = millis();

        if ((now - lastTurn) >= turnDelayTotal) {

          if (turnState == 0) {
            //stop for a moment
            rightMotor(0);
            leftMotor(0);
            lastTurn = now;
            turnDelayTotal = turnDelay;
            turnState = 1;
          }

          else if (turnState == 1) {
            //back up
            rightMotor(-255);
            leftMotor(-255);
            lastTurn = now;
            turnDelayTotal = backupTime;
            turnState = 2;
          }

          else if (turnState == 2) {
            //turn away from obstacle
            rightMotor(255);
            leftMotor(-255);
            lastTurn = now;
            turnDelayTotal = turnTime;
            turnState = 3;
          }
          else if (turnState == 3){
            turnState = 0;
            turning = false;
          }

        }

      } else {
        rightMotor(255);
        leftMotor(255);
      }

    } else {  //if the switch is off then stop
      //stop the motors
      rightMotor(0);
      leftMotor(0);
    }

  } else {
    digitalWrite(ledPin, HIGH);
    if (firstTime) {
      firstTime = false;
      rightMotor(0);
      leftMotor(0);
    }

    if (carState == receiving && digitalRead(switchPin) == LOW) {
      if (Serial.available() > 0) {
        // read the incoming byte:
        incomingByte = Serial.read();
      }
      if (incomingByte == 0x21) {
        carState = idle;
      }

    } else if (carState == idle) {

      if (Serial.available() > 0) {
        // read the incoming byte:
        incomingByte = Serial.read();
      }

      if (incomingByte == 0x35) {
        carState = move;
        lastDrive = millis();
      }

    } else if (carState == move) {
      if (Serial.available() > 0) {
        incomingByte = Serial.read();
      }

      if (incomingByte == 0x66) {
        rightMotor(255);
        leftMotor(255);
        infoString = "Forwards for ";
        sendInfo(infoString);
        firstTimeInfo = true;
        carState = moveFor;

      } else if (incomingByte == 0x62) {
        rightMotor(-255);
        leftMotor(-255);
        infoString = "Backwards for ";
        sendInfo(infoString);
        firstTimeInfo = true;
        carState = moveFor;

      } else if (incomingByte == 0x6c) {
        rightMotor(-255);
        leftMotor(255);
        infoString = "Left for ";
        sendInfo(infoString);
        firstTimeInfo = true;
        carState = moveFor;

      } else if (incomingByte == 0x72) {
        rightMotor(255);
        leftMotor(-255);
        infoString = "Right for ";
        sendInfo(infoString);
        firstTimeInfo = true;
        carState = moveFor;
      }

    } else if (carState == moveFor) {

      if (Serial.available() > 0) {
        incomingDriveDistance = Serial.read();
      }

      driveDistance = (int)incomingDriveDistance;
      drivePeriod = abs(driveDistance) * driveTimePerCm;

      if (firstTimeInfo) {
        infoString = (String)abs(driveDistance) + "cm.";
        sendInfo(infoString);
        firstTimeInfo = false;
      }

      now = millis();
      if (now - lastDrive > drivePeriod) {
        leftMotor(0);
        rightMotor(0);
        carState = receiving;
      }
    }
  }
}

/********************************************************************************/
void rightMotor(int motorSpeed)  //function for driving the right motor
{
  motorSpeed = -motorSpeed;
  if (motorSpeed > 0)  //if the motor should drive forward (positive speed)
  {
    digitalWrite(AIN1, HIGH);  //set pin 1 to high
    digitalWrite(AIN2, LOW);   //set pin 2 to low
  } else if (motorSpeed < 0)   //if the motor should drive backward (negative speed)
  {
    digitalWrite(AIN1, LOW);   //set pin 1 to low
    digitalWrite(AIN2, HIGH);  //set pin 2 to high
  } else                       //if the motor should stop
  {
    digitalWrite(AIN1, LOW);  //set pin 1 to low
    digitalWrite(AIN2, LOW);  //set pin 2 to low
  }
  analogWrite(PWMA, abs(motorSpeed));  //now that the motor direction is set, drive it at the entered speed
}

/********************************************************************************/
void leftMotor(int motorSpeed)  //function for driving the left motor
{
  if (motorSpeed > 0)  //if the motor should drive forward (positive speed)
  {
    digitalWrite(BIN1, HIGH);  //set pin 1 to high
    digitalWrite(BIN2, LOW);   //set pin 2 to low
  } else if (motorSpeed < 0)   //if the motor should drive backward (negative speed)
  {
    digitalWrite(BIN1, LOW);   //set pin 1 to low
    digitalWrite(BIN2, HIGH);  //set pin 2 to high
  } else                       //if the motor should stop
  {
    digitalWrite(BIN1, LOW);  //set pin 1 to low
    digitalWrite(BIN2, LOW);  //set pin 2 to low
  }
  analogWrite(PWMB, abs(motorSpeed));  //now that the motor direction is set, drive it at the entered speed
}

/********************************************************************************/
unsigned long echoTime;  //variable to store the time it takes for a ping to bounce off an object
//RETURNS THE DISTANCE MEASURED BY THE HC-SR04 DISTANCE SENSOR

float getDistance() {
  float calculatedDistance;  //variable to store the distance calculated from the echo time

  //send out an ultrasonic pulse that's 10ms long
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  echoTime = pulseIn(echoPin, HIGH);                 //use the pulsein command to see how long it takes for the
                                                     //pulse to bounce back to the sensor
  calculatedDistance = ((echoTime * 0.0343) / 2.0);  //calculate the distance of the object that reflected the pulse (half the bounce time multiplied by the speed of sound)
  return calculatedDistance;                         //send back the distance that was calculated
}

void checkCarMode() {
  currentState = digitalRead(buttonPin);
  if (currentState != lastFlickerableState) {
    // reset the debouncing timer
    lastDebounceTime = millis();
    lastFlickerableState = currentState;
  }
  if ((millis() - lastDebounceTime) > debounceDelay) {
    if (lastSteadyState == HIGH && currentState == LOW) {
      firstTime = true;
      remote = !remote;
      turnState = 0;
      turning = false;
    }
    lastSteadyState = currentState;
  }
}

void sendEcho() {
  Serial.write(0x21);
  Serial.write(0x34);
  Serial.write(echoTime >> 24);
  Serial.write(echoTime >> 16);
  Serial.write(echoTime >> 8);
  Serial.write(echoTime);
}

void sendInfo(String infoString) {
  Serial.write(0x21);
  Serial.write(0x30);
  int l = infoString.length();
  Serial.write(l >> 8);
  Serial.write(l);

  for (int i = 0; i < l; i++) {
    Serial.write(infoString[i]);
  }
}
