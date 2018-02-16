#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>

#include <Wire.h>

#define DEBUG true

#define GAS A1
#define lightPin A0
#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

const byte slaveID = 2;
unsigned long int dhtTime;
// The DHT needs a cool down period of at least 1 second.
int dhtInterval = 2000;

void setup() {
  if (DEBUG){
    Serial.begin(9600);
    Serial.println("Setting up");
  }
  // Set up i/o
  pinMode(lightPin, INPUT);
  pinMode(GAS, INPUT);
  // i2c as slave
  Wire.begin(slaveID);
  Wire.onRequest(requestEvent);
  // dht sensor
  dht.begin();
  dhtTime = millis();
  if (DEBUG){
    Serial.println("Done!");
  }
}

// Variables for the main loop
int light;
int light_perc;
float light_scale;
int humid, temp, smoke, smoke_perc;

void loop() {
  readSensors();
  // Print to console
  if (DEBUG){
      debugPrint();
  }
  delay(500);
}

void requestEvent(){
  if (DEBUG){
    Serial.println("Request recieved!");
  }
  readSensors();  // Read sensors before sending values.
  Wire.write(temp);
  Wire.write(humid);
  sendInteger(light);
  sendInteger(smoke);
}

void sendInteger(int intValue){
    byte bufferArray[2];
    bufferArray[0] = (intValue >> 8) & 0xFF;    // Shift hight byte to low bytes position (right)
                                                // and remove high byte by anding it with
                                                // 0xFF ie. 0000000011111111
    bufferArray[1] = intValue & 0xFF;           // Get the low byte he same way, but don't shift
    /*
    Send off the bytes, notice that we send high bit first since this makes it
    easier to shift back, since all we need to do is insert high byte,
    is shifting it 8 places to the left and then insert low bit */
    Wire.write(bufferArray, 2);
}

void readSensors(){
  // Read Light
  light = analogRead(lightPin);
  light_scale = light / 1024.0;
  light_perc = light_scale * 100;

  // Read temp/humid
  // The DHT needs a cool down period of at least 1 second.
  if (millis() >= dhtTime){
      if (DEBUG) Serial.println("Reading DHT11");
      humid = dht.readHumidity();
      temp = dht.readTemperature();
      dhtTime = millis() + dhtInterval;
  }

  // Read Smoke value
  smoke = analogRead(GAS);
  float smoke_scalar = smoke / 1024.0;
  smoke_perc = smoke_scalar * 100;
}

void debugPrint(){
  Serial.print("Light value: ");
  Serial.print(light, DEC);
  Serial.print(" | Perc: ");
  Serial.print( light_perc );
  Serial.println("%");

  Serial.print("Temp: ");
  Serial.print(String(temp));
  Serial.print("*C | Humidity: ");
  Serial.println(String(humid));
  Serial.print("Smoke: ");
  Serial.print(smoke, DEC);
  Serial.print(" (");
  Serial.print(smoke_perc);
  Serial.println("%)");
  Serial.println();
}
