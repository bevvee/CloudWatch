// ESP8266 + DHT11 - compatible avec ColdWatch sans clé API (HTTP local)
#include <DHT.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>
#define DHTTYPE DHT11
const char* ssid = "Et@ehei";
const char* password = "eheio2023";
const char* serverName = "http://10.9.9.185:8000/api/post";
#define dht_dpin 12
DHT dht(dht_dpin, DHTTYPE);
void setup() {
  dht.begin(); Serial.begin(9600); WiFi.mode(WIFI_STA); WiFi.begin(ssid, password);
  int attempts=0;
  while (WiFi.status()!=WL_CONNECTED && attempts++<20) {delay(1000);Serial.println("Connecting to WiFi...");}
  if(WiFi.status()==WL_CONNECTED){Serial.println("Connected to WiFi");Serial.println(WiFi.localIP());}
}
void loop() {
  if(WiFi.status()!=WL_CONNECTED){WiFi.disconnect();WiFi.begin(ssid,password);delay(5000);return;}
  float humidity=dht.readHumidity(), temperature=dht.readTemperature();
  if(isnan(humidity)||isnan(temperature)){Serial.println("DHT11 reading failed!");delay(2000);return;}
  WiFiClient client; HTTPClient http; DynamicJsonDocument jsonDoc(200);
  jsonDoc["temp"]=temperature;jsonDoc["hum"]=humidity;
  String jsonStr;serializeJson(jsonDoc,jsonStr);
  if(http.begin(client,serverName)){
    http.addHeader("Content-Type","application/json");
    Serial.println(jsonStr);int code=http.POST(jsonStr);Serial.println(code);
    if(code>0)Serial.println(http.getString());else Serial.println(http.errorToString(code));
    http.end();
  }
  delay(1200000); // pour tests ; utiliser 1200000 pour 20 minutes
}
