
/*  OctoWS2811 Current Test

Lights up all rows in sequence (LED 0 on all strips, then
LED 0 and 1, etc.)

Continually blink the onboard LED to show that the program
is alive and well.

*/

#include <OctoWS2811.h>

const int ledPin = 13;
const int ledsPerStrip = 72;

DMAMEM int displayMemory[ledsPerStrip*6];
int drawingMemory[ledsPerStrip*6];

const int config = WS2811_GRB | WS2811_800kHz;
const int buttonPin = 2;     // the number of the pushbutton pin for Teensy 3.0
unsigned long lastBlink = millis();
bool teensyLED = false;

OctoWS2811 leds(ledsPerStrip, displayMemory, drawingMemory, config);

void setup() {
  // initialize the pushbutton pin as an input:
  pinMode(buttonPin, INPUT);
  pinMode(ledPin, OUTPUT);
  leds.begin();
  
  // Wait 2s before starting loop and clear the LEDs during that time.
  digitalWrite(ledPin, HIGH);
  delay(1000);
  digitalWrite(ledPin, LOW);
  // Clear all LEDs
  for (int i=0; i < leds.numPixels(); i++) {
      leds.setPixel(i, 0x000000);
  }
  leds.show();
  delay(1000);
}

void loop() {
  bool simple = false;
  if (simple) {
    // Reset all the LEDs
    for (int i=0; i < leds.numPixels(); i++) {
        leds.setPixel(i, 0xFFFFFF);
    }
    leds.show();
    return;
  }

  unsigned long ledsLit = 0;
  while (ledsLit < ledsPerStrip) {
    // Light up all strips at once
    for ( int strip = 0; strip < 8; strip ++ ) {
      leds.setPixel(ledsLit + ledsPerStrip * strip, 0xFFFFFF);
      ledsLit ++;
    }
    leds.show();
    delay(100);
    
    unsigned long nowMillis = millis();
    if ( nowMillis - lastBlink > 1000 ) {
        lastBlink = nowMillis;
        teensyLED = !teensyLED;
        digitalWrite(ledPin, teensyLED ? HIGH : LOW);
    }

  }
}
