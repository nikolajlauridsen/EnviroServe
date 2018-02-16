#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>
#include <Wire.h>

const byte sensorID = 2;
const char* ssid="YOUR_SSID";
const char* password = "YOUR_WIFI_PASS";
const byte ledPin = 13;
const byte statusIndicator = 12;
const byte btn = 4;
HTTPClient http;

long unsigned int sendTime;
long unsigned int btnRdy;
int btnCooldown = 10000;
long unsigned int sendInterval = 120000;

void setup() {
  // Start with Serial, for debug.
  Serial.begin(9600);
  Serial.println("Setting up.");
  // Set up pins.
  pinMode(btn, INPUT);
  pinMode(ledPin, OUTPUT);
  pinMode(statusIndicator, OUTPUT);
  digitalWrite(ledPin, LOW);
  digitalWrite(statusIndicator, LOW);
  // Then i2c
  Serial.println("Setting up I2C");
  Wire.begin(2,14);
  Wire.setClockStretchLimit(40000);
  btnRdy = millis();
  sendTime = millis() + sendInterval;
  Serial.println("Setup complete");
  // After lastly set up the wifi as a seperate setup routine
  setupWiFi();
}

byte temp, humid;
int light, smoke;
byte count;
void loop() {
  // Check button state
  if (digitalRead(btn) == LOW){
      // Check if button has 'cooled down', don't want to spam server.
      if (millis() >= btnRdy){
          Serial.println("User override, moving up transmit.");
          sendTime = millis();              // Update trigger for send state to now.
          btnRdy = millis() + btnCooldown;  // Update cooldown trigger.
      }

  }
  // Check the send state
  if (millis() >= sendTime){
      digitalWrite(statusIndicator, HIGH);  // Indicate we're working on tramitting.
      requestData();                        // Request data from i2c slave.
      debugPrint();                         // Debug terminal print.
      sendData();                           // Send the data over WiFi.
      sendTime = millis() + sendInterval;   // Update trigger for send state.
      digitalWrite(statusIndicator, LOW);   // Indicate that we're done.
  }
}

void setupWiFi(){
  Serial.print("\nConnecting to: ");
  Serial.println( ssid );
  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("\nConnecting");
  // Wait for WiFi status to be true.
  while(WiFi.status() != WL_CONNECTED){
    digitalWrite(statusIndicator, HIGH);
    delay(250);
    digitalWrite(statusIndicator, LOW);
    delay(250);
    Serial.print(".");
  }
  // We're out of the loop, sucess!
  digitalWrite(ledPin, HIGH);
  Serial.println("\nWiFi connected!");
  Serial.print("Node IP: ");
  Serial.println(WiFi.localIP());  // Get and print local ip
}

void requestData(){
    Serial.println("\nRequesting data");
    Wire.requestFrom(sensorID, 6);
    count = 0;
    while(Wire.available()){
      switch(count){
          case 0:  // first byte ie temp.
              temp = Wire.read();
              count++;
              break;
          case 1:  // Second byte: humid.
              humid = Wire.read();
              count++;
              break;
          case 2:  // Light value, double byte.
              light = recieveInteger();
              count++;
              break;
          case 3:  // Smoke value, double byte.
              smoke = recieveInteger();
              count++;
              break;
      }
   }
}

int recieveInteger(){
    byte high, low;     // Our high and low bytes
    int returnInt;      // Int variable to hold our value
    // I'm assume we've already requested the value (This might end badly)
    high = Wire.read();
    low = Wire.read();
    returnInt = high;
    returnInt = (returnInt<<8)|low;
    return returnInt;
}

String parseURL(/* arguments */) {
    /*
    Parses the current climate value into a url string for our server
    This is a real mess, but meh it does the job.
    */
    String url = "http://192.168.1.250:2020/climate/data?";
    // Sensor ID first
    url = url + "sensor_id=";
    url = url + sensorID;
    url = url + "&temp=";
    url = url + temp;
    url = url + "&humid=";
    url = url + humid;
    url = url + "&light=";
    url = url + light;
    url = url + "&smoke=";
    url = url + smoke;
    return url;
}

void sendData(){
    // Parse latest values into url parameters.
    Serial.print("Parsing url.. ");
    String url = parseURL();
    Serial.println(url);
    // Send it off
    Serial.println("Beginning http connection");
    http.begin(url);
    Serial.println("Sending request");
    int statusCode = http.POST((uint8_t *)"Arduino sensor",2);
    if (statusCode == HTTP_CODE_OK){
      Serial.print("Status code: ");
      Serial.println(statusCode);
      String res = http.getString();
      Serial.println(res);
      digitalWrite(ledPin, HIGH);

    } else {
      Serial.print("Error : ");
      Serial.println(statusCode, DEC);
      digitalWrite(ledPin, LOW);
    }
    Serial.println("Closing connection.");
    http.end();
}

void debugPrint(){
    Serial.println("Data recieved:");
    Serial.print("Temp: ");
    Serial.print(temp, DEC);
    Serial.print("*C | Humidity: ");
    Serial.print(humid, DEC);
    Serial.println("%");
    Serial.print("Light: ");
    Serial.println(light, DEC);
    Serial.println("Smoke: ");
    Serial.println(smoke, DEC);
    Serial.println("\nSending it off.");
}
