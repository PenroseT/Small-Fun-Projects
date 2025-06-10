#include <Arduino.h>
#define IR_SEND_PIN 4
#define SIGNAL_PIN 5
#define DISABLE_CODE_FOR_RECEIVER
#include <Vector.h>
#include <Streaming.h>
#include <IRremote.hpp>

#define ELECTRA_KHZ 38

// Each signal is specified by 34 bits
// that need to be encoded with Manchester encoded
// before they are sent 
#define SIGNAL_SIZE 34

// Each bit of the Manchester encoding corresponds to maximum 
// number of 2 integers that specify LOW and HIGH voltage duration.
// Signal beginning is specified by one long HIGH followed by one 
// long LOW. Since each signal is sent three times, maximum number
// of integers (durations) to be sent is 3*2*34+3*2=210
#define MAX_SIZE 210

// Averaging over lengths of unit signals gave a value that
// is approximately 992
#define UNIT 992

// Each signal begins with a high and a low of durations ~3000us.
// The numbers below were obtained by averaging over many signals
// sent by Electra remote
#define BEGIN_HIGH 3032 
#define BEGIN_LOW 2868

// Defining a Vector type that will store rawData
// to be sent using IRremote library
typedef Vector<unsigned int> rawSignal;
static unsigned int signalStorageArray[MAX_SIZE];

// Initializing flags to be used by the routine
// that converts bit arrays into signal vectors
static bool CHANGE_FLAG=0;
static bool EXTEND=0;
static bool DIF;
static bool START;

// Each signal is sent 3 times
const uint8_t SIGNAL_NO = 3;

typedef enum ACmode{
  // All binary numbers are written most signficant bit first
  // to make reading out digits more natural in the code

  coolMode = 0b100,
  hotMode = 0b010,
  autoMode = 0b110,
  dryMode = 0b001,
  fanMode = 0b101
} ACmode;

typedef enum FanSpeed{
  
  fanSlow = 0b00,
  fanMedium = 0b10,
  fanFast = 0b01,
  fanAuto = 0b11

} FanSpeed;

void setup() {
  // put your setup code here, to run once:
  pinMode(IR_SEND_PIN, OUTPUT);
  pinMode(SIGNAL_PIN, OUTPUT);
  IrSender.begin(DISABLE_LED_FEEDBACK);
  Serial.begin(9600);
}

bool* createBitArray(bool* bitArray, bool power, ACmode mode, FanSpeed fan,
                     bool swing, bool tilt, unsigned int temp, bool sleep){


  // POWER ON - 0 POWER OFF 1
  bitArray[0] = power;

  // AC operation mode is defined with three bits
  for(int i=1; i<4; i++){
    bitArray[i]=mode%2;
    mode = mode/2;
  }

  // Fan speed is defined with two bits
  for(int i=4; i<6; i++){
    bitArray[i]=fan%2;
    fan = fan/2;
  }

  // Basic operation (zero); TILT_STEP=1, TILT_STEP=0; SWING ON=1, SWING OFF =0; (two zeros) 
  bitArray[6] = 0;
  bitArray[7] = tilt;
  bitArray[8] = swing;
  bitArray[9] = 0;
  bitArray[10] = 0;

  // Temperature goes from 16 to 30 degrees C, and it is represented by
  // binary numbers from 0b0001 to 0b1111
  // Mapping that maps 30 degrees to 1, 29 to 2, and so on
  // up to 16 that maps to 15, so that most significant bit
  // comes first

  unsigned int _temp = temp - 15;
  //unsigned int _temp = temp-15;
  for(int i=14; i>10; i--){
    bitArray[i] = _temp%2;
    _temp = _temp/2;
  }
  
  bitArray[15] = sleep;

  // Basic operation has 16 zeros followed by 1 and 0
  for(int i=16; i<32; i++){
    bitArray[i] = 0;
  }

  bitArray[32] = 1;
  bitArray[33] = 0;

  return bitArray;
}

void printBitArray(bool* signal, int printSpeed = 50){

  for(auto value = signal; value-signal<SIGNAL_SIZE; value++){
    Serial << *value << " ";
    delay(printSpeed);
  }

  Serial << "\n";
}

rawSignal bitArrayToRawData(bool* bitArray){

  rawSignal signal;
  signal.setStorage(signalStorageArray);

  // Each signal is repeated SIGNAL_NO times
  for(int i=0; i<SIGNAL_NO; i++){

    EXTEND ? (signal.push_back(BEGIN_HIGH+UNIT)): (signal.push_back(BEGIN_HIGH));


    if(!bitArray[0]){
      signal.push_back(BEGIN_LOW);
      START=0;
    } else if(bitArray[0]){
      signal.push_back(BEGIN_LOW+UNIT);
      DIF = (bitArray[1]^bitArray[0]);
      if(!DIF){
        signal.push_back(UNIT);
      } else if(DIF){
        CHANGE_FLAG=1;
      }
      START=1;
    }

    for(int j=START; j<SIGNAL_SIZE-1; j++){
      DIF = (bitArray[j+1]^bitArray[j]);
      
      if(!CHANGE_FLAG){
        if(!DIF){
          signal.push_back(UNIT);
          signal.push_back(UNIT);
        } else if(DIF){
          signal.push_back(UNIT);
        }
      } else if(CHANGE_FLAG){
          signal.push_back(2*UNIT);
        if(!DIF){
          signal.push_back(UNIT);
        } else if(DIF){

        }
      }

    CHANGE_FLAG = DIF;
    }

    // For first two signals that are sent the next beginning mark should be
    // extended. Although the last bit is probably always supposed to be 0,
    // this routine should cover all possible cases to avoid unexpected
    // behavior.

    
    
    if(!CHANGE_FLAG){
      if(!bitArray[SIGNAL_SIZE-1]){
        signal.push_back(UNIT);
        signal.push_back(UNIT);
        EXTEND=0;
      } else if(bitArray[SIGNAL_SIZE-1]){
        signal.push_back(UNIT);
        EXTEND=1;
      }
    } else if(CHANGE_FLAG){
      if(!bitArray[SIGNAL_SIZE-1]){
        signal.push_back(2*UNIT);
        signal.push_back(UNIT);
        EXTEND=0;
      } else if(bitArray[SIGNAL_SIZE-1]){
        signal.push_back(2*UNIT);
        EXTEND=1;
      }
    }
    

    CHANGE_FLAG = 0;
    START = 0;
  }

  signal.push_back(BEGIN_HIGH+UNIT);
  // EXTEND ? (signal.push_back(BEGIN_HIGH+UNIT)): (signal.push_back(BEGIN_HIGH));
  // signal.push_back(BEGIN_LOW);

  CHANGE_FLAG = 0;
  EXTEND = 0;

  return signal;
}

void printSignal(rawSignal signal, int printSpeed=50){

  for(unsigned int element: signal){
    Serial << element << " ";
    delay(printSpeed);
  }

  Serial << "\n";
}

void blink(unsigned int delayTime = 20, unsigned int blinkNumber=1){

  for(unsigned int i=0; i<blinkNumber; i++){
    digitalWrite(SIGNAL_PIN, HIGH);
    delay(delayTime);
    digitalWrite(SIGNAL_PIN, LOW);
    delay(delayTime);
  }
}


void loop() {
  // put your main code here, to run repeatedly:
  bool power = 0;
  ACmode mode = coolMode;
  FanSpeed speed = fanFast;
  unsigned int temp = 22;
  bool swing = 0;
  bool tilt = 0;
  bool sleep = 0;

  bool signal_array[SIGNAL_SIZE];
  bool* bit_array = createBitArray(signal_array, power, mode, speed,
                                   swing, tilt, temp, sleep);

  rawSignal signal = bitArrayToRawData(bit_array);

  // printBitArray(bit_array, 20);
  // printSignal(signal, 20);
  // Serial << sizeof(signal.data()) << endl;
  // Serial << signal.size() << endl << endl;
  // Serial << "Send!" << endl;

  blink(50, 1);

  IrSender.sendRaw(signal.data(), signal.size(), ELECTRA_KHZ);

  blink(30, 3);

  delay(3500);


}
