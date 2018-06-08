
#include "Arduino.h"

#define PACKET_SIZE 15

int outPin1= 5;
int outPin2 = 6;
int outPin3 = 7;
int scanReg[3];
int checkoutReg[3];
int outputPins[3] = {outPin1, outPin2, outPin3};
byte buffer[PACKET_SIZE];
int DELAY = 10000;

void setup() {
  pinMode(outPin1, OUTPUT);
  pinMode(outPin2, OUTPUT);
  pinMode(outPin3, OUTPUT);
  Serial.begin(115200);
  Serial1.begin(115200);
  Serial2.begin(115200);
  Serial3.begin(115200);
  turnOffAll();
}

void turnOnAll()
{
  for(int i=0;i<3;i++)
  {
    digitalWrite(outputPins[i], LOW);
    } 
}

void turnOffAll()
{
  for(int i=0;i<3;i++)
  {
    digitalWrite(outputPins[i], HIGH);
    }  
}

void loop() {
  if(Serial.available())
  {
    byte cmd = Serial.read();
    switch(cmd)
    {
      case 0x00:
        initSystem();  
        break;
      case 0x01: //getStatus
        break;
      case 0x10: //scan
        doScan();
        break;
      default:
        break;
    }
  }
  int mode = 0x11;
  manageScanCheckout(&Serial1, 1, mode);
  manageScanCheckout(&Serial2, 2, mode);
  manageScanCheckout(&Serial3, 3, mode);
}

void doScan()
{
  int mode = 0x10;
  turnOn();
  delay(DELAY);
  manageScanCheckout(&Serial1, 1, mode);
  manageScanCheckout(&Serial2, 2, mode);
  manageScanCheckout(&Serial3, 3, mode);
  turnOff();
}

void manageScanCheckout(HardwareSerial *serial, int regNum, int mode)
{
  if(checkoutReg[regNum-1] == 1)
    {
      performReadWrite(serial, regNum, 0x11);  
    }
  if(scanReg[regNum-1] == 1)
    {
      performReadWrite(serial, regNum, 0x10);  
    }   
}

void performReadWrite(HardwareSerial *serial, int regNum, int startByte)
{
  //int now = millis();
  int x = 0;
  int len = 0;
  bool didSend = false;
  while(serial->available())
  {
    x = serial->read(); //first byte should be 0x0A
    //Serial.write(serial->read());
    //if(false)
    if(x == 0xa0) //found first byte of response
    {
        delay(500);
        buffer[0] = startByte;
        buffer[1] = regNum;
        len = serial->read(); // len
        if(len - 19 != 0){
          continue;
          }
        serial->read(); // address
        serial->read(); // cmd should be 89
        serial->read(); // freqAnt
        serial->read(); // PC 1/2
        serial->read(); // PC 2/2
      
        for(int i=2;i<PACKET_SIZE;i++)
        {
          buffer[i] = serial->read();  
        }

        buffer[14] = x;
        Serial.write(buffer, PACKET_SIZE);
        //Serial.write('\n');
        //Serial.flush();
        didSend = true;
        serial->read(); //
        serial->read(); //Checksum
    }
    //delay(500);
    //if(now - millis() > DELAY){
      // break;
    //}
  }
  if(didSend){
    Serial.write('\n');
    didSend = false;
    //serial->flush();
    }

}


void turnOn()
{
  for(int i=0; i<3;i++)
  {
    if(scanReg[i] == 1)
    {
      digitalWrite(outputPins[i], LOW);
    }
  }
}

void turnOff()
{
  for(int i=0; i<3;i++)
  {
    if(scanReg[i] == 1)
    {
      digitalWrite(outputPins[i], HIGH);
    }
  }
}  


void initSystem()
{
  turnOnAll();
  delay(500);
  turnOffAll();
  
  //assume 00 is received here
  int scanCtr = 0;
  int coCtr = 0;
  //clear
  memset(scanReg, 0, 3*sizeof(int));
  memset(checkoutReg, 0, 3*sizeof(int));
  for(int i=0; i<3; i++)
  {
    byte x = Serial.read();
    if(x == 0x00)
    {
      scanReg[i] = 0;
      checkoutReg[i] = 1;
      digitalWrite(outputPins[i], LOW);
      
    }  
    else if(x==0x01)
    {
       scanReg[i] = 1;
       checkoutReg[i] = 0;
    }
    //ignore if not 0x00 or 0x01
  } 

  //flush 0x0a
  while(Serial.available())
  {
    Serial.read();
  }
}  

