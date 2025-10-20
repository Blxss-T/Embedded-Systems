#include <Servo.h>
#define x_pin A0
#define y_pin A1
#define hardcoded_vcc A2
#define hardcoded_gnd A3

Servo myServo;

int servoPin = 6;
int angle = 90;          // Start in the middle
int lastAngle = 90;      // For smooth motion

void setup() {
  Serial.begin(9600);
  pinMode(hardcoded_vcc, OUTPUT);
  pinMode(hardcoded_gnd, OUTPUT);
  digitalWrite(hardcoded_vcc, HIGH);
  digitalWrite(hardcoded_gnd, LOW);

  myServo.attach(servoPin);
  myServo.write(angle);
  delay(1000);
}

void loop() {
  int x_val = analogRead(x_pin);
  int y_val = analogRead(y_pin);

  // Map joystick X to servo angle (left-right movement)
  angle = map(x_val, 0, 1023, 0, 180);

  // Optional: dead zone (prevents servo shaking when joystick is near center)
  if (abs(angle - lastAngle) > 2) {
    myServo.write(angle);
    lastAngle = angle;
  }

  Serial.print("Joystick: (");
  Serial.print(x_val);
  Serial.print(", ");
  Serial.print(y_val);
  Serial.print(") | Servo angle: ");
  Serial.println(angle);

  delay(100);
}
