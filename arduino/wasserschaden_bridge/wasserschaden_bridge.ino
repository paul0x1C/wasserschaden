#include <Arduino.h>
#include <painlessMesh.h>
#include <PubSubClient.h>
#include <WiFiClient.h>
#include "settings.cpp" //contains passwords

#define   MESH_PORT       5555

#define HOSTNAME "MQTT_Bridge"

// Prototypes
void receivedCallback( const uint32_t &from, const String &msg );
void mqttCallback(char* topic, byte* payload, unsigned int length);
void mqttConnect();

char* message_buff;

IPAddress getlocalIP();

IPAddress myIP(0,0,0,0);
IPAddress mqttBroker(10, 10, 10, 23);

painlessMesh  mesh;
WiFiClient wifiClient;
PubSubClient mqttClient(mqttBroker, 1883, mqttCallback, wifiClient);

Scheduler userScheduler;
Task reconnect(1000, TASK_FOREVER, &mqttConnect);


char* convert_for_mqtt(int input){
  String pubString = String(input);
  pubString.toCharArray(message_buff, pubString.length()+1); 
  return message_buff;
}

void setup() {
  Serial.begin(115200);

  mesh.setDebugMsgTypes( ERROR | STARTUP | CONNECTION );  // set before init() so that you can see startup messages

  // Channel set to 6. Make sure to use the same channel for your mesh and for you other
  // network (STATION_SSID)
  mesh.init( MESH_PREFIX, MESH_PASSWORD, MESH_PORT, WIFI_AP_STA, 1);
  mesh.onReceive(&receivedCallback);
  
  mesh.onNewConnection([](const uint32_t nodeId) {
    if(nodeId != 0){
      String topic = "painlessMesh/from/" + String(nodeId);
      mqttClient.publish((topic.c_str()), "connected");
      Serial.printf("New Connection \n", nodeId);
    }
  });

  mesh.onDroppedConnection([](const uint32_t nodeId) {
    if(nodeId != 0){
      String topic = "painlessMesh/from/" + String(nodeId);
      mqttClient.publish(topic.c_str(), "dropped");
      Serial.printf("Dropped Connection %u\n", nodeId);
    }
  });

  mesh.stationManual(STATION_SSID, STATION_PASSWORD);
  mesh.setHostname(HOSTNAME);

  userScheduler.addTask(reconnect);
}

void mqttConnect(){
  if (mqttClient.connect("pmC")) {
      Serial.println("connected to mqtt");
      mqttClient.publish("painlessMesh/from/gateway","Ready!");
      mqttClient.subscribe("painlessMesh/to/#", 0);
      reconnect.disable();
  }
}

void loop() {
  mesh.update();
  mqttClient.loop();

  if(myIP != getlocalIP()){
    myIP = getlocalIP();
    Serial.println("My IP is " + myIP.toString());
    mqttConnect();
  }
  if(!mqttClient.connected() and !reconnect.isEnabled()) {
    reconnect.enable();
    Serial.println("enabled reconnect task");
  }
  userScheduler.execute();
}

void receivedCallback( const uint32_t &from, const String &msg ) {
  Serial.printf("bridge: Received from %u msg=%s\n", from, msg.c_str());
  String topic = "painlessMesh/from/" + String(from);
  mqttClient.publish(topic.c_str(), msg.c_str());
}

void mqttCallback(char* topic, uint8_t* payload, unsigned int length) {
  char* cleanPayload = (char*)malloc(length+1);
  payload[length] = '\0';
  memcpy(cleanPayload, payload, length+1);
  String msg = String(cleanPayload);
  free(cleanPayload);

  String targetStr = String(topic).substring(16);

  if(targetStr == "gateway")
  {
    if(msg == "getNodes")
    {
      //Serial.println( mesh.subConnectionJson().c_str());
      mqttClient.publish("painlessMesh/from/gateway", mesh.subConnectionJson().c_str());
    }
  }
  else if(targetStr == "broadcast") 
  {
    mesh.sendBroadcast(msg);
  }
  else
  {
    uint32_t target = strtoul(targetStr.c_str(), NULL, 10);
    if(mesh.isConnected(target))
    {
      mesh.sendSingle(target, msg);
    }
    else
    {
      mqttClient.publish("painlessMesh/from/gateway", "Client not connected!");
    }
  }
}

IPAddress getlocalIP() {
  return IPAddress(mesh.getStationIP());
}
