#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>

#include <Wire.h>
#include <LiquidCrystal.h>

#define DEBUG true

#define GAS A1
#define lightPin A0
#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);
LiquidCrystal lcd(7, 8, 9, 10, 11, 12);

const byte slaveID = 2;
const byte leftBtn = 3;
const byte centerBtn = 4;
const byte rightBtn = 5;
const byte lcdBackLight = 6;
bool lcdState;
bool centerState = false;
unsigned long int dhtTime;
unsigned long int goTime;
// The DHT needs a cool down period of at least 1 second.
int dhtInterval = 2000;
int idleTime = 1000;

void setup() {
  if (DEBUG){
    Serial.begin(9600);
    Serial.println("Setting up");
  }
  // Set up i/o
  pinMode(lightPin, INPUT);
  pinMode(GAS, INPUT);
  pinMode(centerBtn, INPUT);
  pinMode(lcdBackLight, OUTPUT);
  digitalWrite(lcdBackLight, HIGH);
  lcdState = true;
  // i2c as slave
  Wire.begin(slaveID);
  Wire.onRequest(requestEvent);
  // dht sensor
  dht.begin();
  dhtTime = millis();
  goTime = millis();
  // Screen
  lcd.begin(16, 2);
  lcd.setCursor(0, 0);
  lcd.write("Hello world!");
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
  // idle job
  if (millis() >= goTime){
    readSensors();
    updateScreen();
    // Print to console
    if (DEBUG){
        debugPrint();
    }
    goTime = millis() + idleTime;
  }

  // On-demand
  bool center_pushed = digitalRead(centerBtn);
  if (center_pushed == LOW){
      if (!centerState){
          // Center state was false, ie. the button has just been pressed
          // Check screen state and switch it
          if(lcdState){
              digitalWrite(lcdBackLight, LOW);
              lcdState = false;
          } else {
              digitalWrite(lcdBackLight, HIGH);
              lcdState = true;
          }
          centerState = true;
      }
  } else {
      centerState = false;
  }

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

void updateScreen(){
    lcd.setCursor(0,0);
    lcd.print("Temp|Light|Smoke");
    lcd.setCursor(1, 1);
    lcd.print(round(temp));
    lcd.setCursor(6, 1);
    lcd.print(round(light_perc));
    lcd.print('%');
    lcd.setCursor(12, 1);
    lcd.print(smoke);
    if (smoke < 100){
        lcd.print(' ');
    }

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
