#include "painlessMesh.h"
#include "settings.cpp" //contains definition of MESH_PREFIX and MESH_PASSWORD
const int flushTime = 150000;
const int valve_pin = D1;
const int status_pin = D2;
const int opened_value = HIGH;
const int closed_value = LOW;

//timeouts for actions when no bridge is found
const int ping_timeout = 30000;
const int reset_timeout = 60000;
boolean con_resent = false;

String msg_open = "opening valve";
String msg_close = "closing valve";
String msg_connected = "con";
String msg_ping = "pong";

boolean blink_state = false;
boolean first_time_adjust = true;

boolean is_open = false;

uint32_t bridge = 0;

long running_since;

Scheduler userScheduler;
painlessMesh  mesh;

// User stub
void sendMessage() ; // Prototype so PlatformIO doesn't complain
void valve();
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
    mesh.sendSingle(from, msg_ping + "|" + is_open);
    pingBlink.enable();
  }
}
void blink(){
  if (pingBlink.isLastIteration()){
    digitalWrite(status_pin, LOW);
    blink_state = false;
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
      mesh.sendBroadcast(msg_connected + "|" + is_open);
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

//mesh.setDebugMsgTypes( ERROR | MESH_STATUS | CONNECTION | SYNC | COMMUNICATION | GENERAL | MSG_TYPES | REMOTE ); // all types on
  mesh.setDebugMsgTypes( ERROR | STARTUP ); 

  mesh.init( MESH_PREFIX, MESH_PASSWORD, &userScheduler, 5555 ); //defined in extra file thats not on github
  mesh.onReceive(&receivedCallback);
  mesh.onNewConnection(&newConnectionCallback);
  mesh.onChangedConnections(&changedConnectionCallback);
  mesh.onNodeTimeAdjusted(&nodeTimeAdjustedCallback);

  userScheduler.addTask( closeValveTask );
  userScheduler.addTask( pingBlink );
  pinMode(status_pin, OUTPUT);
  pinMode(valve_pin, OUTPUT);
  pingBlink.setIterations(2);
  pingBlink.enable();
  running_since = millis();
}

void loop() {
  //ESP.wdtFeed();
  userScheduler.execute();
  mesh.update();
  if(bridge == 0){
    if(millis() - running_since > reset_timeout){
      ESP.reset();
    }else if(millis() - running_since > ping_timeout and !con_resent){
      mesh.sendBroadcast(msg_connected + "|" + is_open);
      con_resent = true;
    }
  }
}
