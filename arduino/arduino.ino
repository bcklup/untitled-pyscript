#include <Arduino.h>

// Relay Pins
int heater_pin = 11;
int stirrer_pin = 13;
int solenoid_pin = 10;

// RGB Pins
int led1 = 9;
int led2 = 8;
int led3 = 7;

// Button Pins
int button1_pin = 2;
int button2_pin = 4;

// Timer Variables
unsigned long LOOP_INTERVALS = 2000;
unsigned long SOLENOID_TIMER = 10000; // Interval between solenoid on->off
unsigned long STAGE_1_TIMER = 30000; // Run stirrer this long before turning on heating element
unsigned long STAGE_1_RUNTIME = 60000; // Runtime while 100deg
unsigned long STAGE_1_PAUSE = 5000; // Pause to cool down
unsigned long STAGE_2_TIMER = 5000; // isolated blend timer for stage 2
unsigned long STAGE_2_RUNTIME = 60000;

bool lock = false;

// Init GPIO to BOARD mode
void setup() {
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
  pinMode(led3, OUTPUT);
  digitalWrite(led1, LOW);
  digitalWrite(led2, LOW);
  digitalWrite(led3, LOW);
  pinMode(heater_pin, OUTPUT);
  pinMode(stirrer_pin, OUTPUT);
  pinMode(solenoid_pin, OUTPUT);
  pinMode(button1_pin, INPUT_PULLUP);
  pinMode(button2_pin, INPUT_PULLUP);
  digitalWrite(heater_pin, HIGH);
  digitalWrite(stirrer_pin, HIGH);
  digitalWrite(solenoid_pin, HIGH);
  Serial.begin(9600);
  digitalWrite(led3, HIGH);
}


void log(String text) {
  Serial.println(text);
}

void stage1_trigger() {
  if (!lock) {
    lock = true;
    digitalWrite(led1, HIGH);
    log("---------------------------------------");
    log("[STAGE 1] Starting...");
    log("[GPIO] Stirrer ON for " + String(STAGE_1_TIMER) + " ms...");
    digitalWrite(stirrer_pin, LOW);

    delay(STAGE_1_TIMER);
    digitalWrite(stirrer_pin, HIGH);

    log("[GPIO] Heater ON");
    digitalWrite(heater_pin, LOW);

    delay(STAGE_1_RUNTIME);
    delay(STAGE_1_RUNTIME);
    delay(STAGE_1_RUNTIME);
    delay(STAGE_1_RUNTIME);
    delay(STAGE_1_RUNTIME);

    log("[STAGE 1] Heating and blending complete.");

    log("[GPIO] Heater OFF");
    digitalWrite(heater_pin, HIGH);

    log("[STAGE 1] Cooling down...");
    delay(STAGE_1_PAUSE);

    digitalWrite(led1, LOW);
    lock = false;

  } else {
    log("[ERR] Another operation is in progress.");
  }
}

void stage2_trigger() {
  if (!lock) {
    lock = true;
    digitalWrite(led2, HIGH);
    log("---------------------------------------");
    log("[STAGE 2] Starting...");

    log("[GPIO] Solenoid ON for " + String(SOLENOID_TIMER) + " ms...");
    digitalWrite(solenoid_pin, LOW);
    delay(SOLENOID_TIMER);
    digitalWrite(solenoid_pin, HIGH);

    log("[GPIO] Stirrer ON for " + String(STAGE_2_TIMER) + " ms...");
    digitalWrite(stirrer_pin, LOW);

    delay(STAGE_2_TIMER);
    digitalWrite(stirrer_pin, HIGH);

    log("[GPIO] Heater ON");
    digitalWrite(heater_pin, LOW);

    delay(STAGE_2_RUNTIME);
    delay(STAGE_2_RUNTIME);
    delay(STAGE_2_RUNTIME);
    delay(STAGE_2_RUNTIME);

    log("[STAGE 1] Heating and blending complete.");
    log("[GPIO] Heater OFF");
    digitalWrite(heater_pin, HIGH);

    log("[STAGE 2] Complete. Restarting system.");
    delay(2000);

    digitalWrite(led2, LOW);
    lock = false;
  } else {
    log("[ERR] Another operation is in progress.");
  }
}

void loop() {
  digitalWrite(led3, HIGH);
  int btn1 = digitalRead(button1_pin);
  int btn2 = digitalRead(button2_pin);
  // log(String(btn1) + ' ' + String(btn2));
  if (!lock) {
    if (btn1 == LOW) {
      stage1_trigger();
    }
    if (btn2 == LOW) {
      stage2_trigger();
    }
  }

  delay(100);  // debounce the button
}
