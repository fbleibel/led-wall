/*
  UsbBandwidth
  Just gobble up as many bytes of data as possible and discard them.
  Also blink the LED regularly to signal data coming in.
*/

// LED pin on Teensy 3.0
int led = 13;

// the setup routine runs once when you press reset:
void setup() {                
  // Note: the baud rate is ignored in the case of Teensy USB
  Serial.begin(9600);
  pinMode(led, OUTPUT);     
}

int bytes_recv = 0;
bool toggle = false;

// the loop routine runs over and over again forever:
void loop() {  
  char buffer[1024];
  int avail = Serial.available();
  int bytesRead = Serial.readBytes(buffer, min(1024, avail));
  bytes_recv += bytesRead;
  // Blink every 1MB received
  if (bytes_recv > 1 << 20) {
    toggle = !toggle;  
    digitalWrite(led, toggle ? HIGH : LOW);
    bytes_recv -= 1 << 20;
  }
}
