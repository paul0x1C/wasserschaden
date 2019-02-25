#include "painlessMesh.h"

#include <OneWire.h>
#include <DallasTemperature.h>

#include "settings.cpp" //contains definition of MESH_PREFIX and MESH_PASSWORD

const int flushTime = 150000;
const int valve_pin = D1;
const int status_pin = D2;
const int sense_pin = D3;
const int temperature_pin = D7;
const int opened_value = HIGH;
const int closed_value = LOW;

//timeouts for actions when no bridge is found
const int ping_timeout = 30000;
const int reset_timeout = 60000;
boolean con_resent = false;

String msg_open = "opening";
String msg_close = "closing";
String msg_connected = "online";
String msg_ping = "pong";
String msg_sense = "sense";

boolean blink_state = false;
boolean first_time_adjust = true;
boolean is_open = false;

uint32_t bridge = 0;

long running_since;

OneWire oneWire(temperature_pin);
DallasTemperature sensors(&oneWire);

Scheduler userScheduler;
painlessMesh  mesh;

// User stub
void sendMessage() ; // Prototype so PlatformIO doesn't complain
void valve();
void blink();
Task closeValveTask(flushTime, 2, &valve);
Task pingBlink(100, 6, &blink);

// Needed for painless library
void receivedCallback( uint32_t from, String &msg ) {
  Serial.printf("startHere: Received from %u msg=%s\n", from, msg.c_str());
  if(msg == "open"){
    bridge = from;
    Serial.println("Received open message");
    open_valve();
  }else if(msg == "close"){
    bridge = from;
    Serial.println("Received close message");
    close_valve();
  }else if(msg == "ping"){
    bridge = from;
    mesh.sendSingle(from, msg_ping);
    pingBlink.enable();
  }else if(msg == "temp"){
    bridge = from;
    sensors.requestTemperatures();
    mesh.sendSingle(from, "t:" + String(sensors.getTempCByIndex(0)));
  }else if(msg == "sense"){
    bridge = from;
    mesh.sendSingle(from, "s:" + String(sense_water()));
  }else if(msg == "state"){
    bridge = from;
    mesh.sendSingle(from, "v:" + String(is_open));
  }else if(msg == "welcome"){
    bridge = from;
  } 
}
void blink(){
  if (pingBlink.isLastIteration()){
    digitalWrite(status_pin, LOW);
    blink_state = true;
    pingBlink.disable();
    pingBlink.setIterations(6);
  }else{
    blink_state = !blink_state;
    digitalWrite(status_pin, blink_state);
    Serial.println(blink_state);
  }
}

void newConnectionCallback(uint32_t nodeId) {
    Serial.printf("--> startHere: New Connection, nodeId = %u\n", nodeId);
}

void changedConnectionCallback() {
    Serial.printf("Changed connections %s\n",mesh.subConnectionJson().c_str());
}

void nodeTimeAdjustedCallback(int32_t offset) {
    Serial.printf("Adjusted time %u. Offset = %d\n", mesh.getNodeTime(),offset);
    if(first_time_adjust){
      mesh.sendBroadcast(msg_connected);
      first_time_adjust = false;
    }
}

void valve(){
   if (closeValveTask.isLastIteration()){
    close_valve();
    closeValveTask.disable();
   }
}

void open_valve(){
  closeValveTask.setIterations(2);
  closeValveTask.enable();
  Serial.println("Opening valve");
  mesh.sendSingle(bridge, msg_open); 
  digitalWrite(valve_pin, opened_value);
  is_open = true;
}

void close_valve(){
  Serial.println("Closing valve");
  mesh.sendSingle(bridge, msg_close); 
  digitalWrite(valve_pin, closed_value);
  closeValveTask.disable();
  is_open = false;
}
void setup() {
  ESP.wdtEnable(5000);
  close_valve();
  Serial.begin(115200);
  
  mesh.setDebugMsgTypes( ERROR | STARTUP ); 
  
  mesh.init( MESH_PREFIX, MESH_PASSWORD, &userScheduler, 5555, WIFI_AP_STA, 4); //defined in extra file thats not on github
  mesh.setContainsRoot();
  mesh.onReceive(&receivedCallback);
  mesh.onNewConnection(&newConnectionCallback);
  mesh.onChangedConnections(&changedConnectionCallback);
  mesh.onNodeTimeAdjusted(&nodeTimeAdjustedCallback);

  sensors.begin();
  
  userScheduler.addTask( closeValveTask );
  userScheduler.addTask( pingBlink );
  pinMode(status_pin, OUTPUT);
  pinMode(valve_pin, OUTPUT);
  pinMode(sense_pin, INPUT);
  pingBlink.setIterations(2);
  pingBlink.enable();
  running_since = millis();
}

boolean sense_water(){
  return !digitalRead(sense_pin);
}

void loop() {
  ESP.wdtFeed();
  userScheduler.execute();
  mesh.update();
  if(bridge == 0){
    if(millis() - running_since > reset_timeout){
      ESP.reset();
    }else if(millis() - running_since > ping_timeout and !con_resent){
      mesh.sendBroadcast(msg_connected);
      con_resent = true;
    }
  }
}
