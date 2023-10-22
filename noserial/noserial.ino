#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include <SD.h>
#include "Adafruit_BMP3XX.h"

#define BMP_SCK 13
#define BMP_MISO 12
#define BMP_MOSI 11
#define BMP_CS 10

#define SEALEVELPRESSURE_HPA (1013.25)

Adafruit_BMP3XX bmp;

/* Set the delay between fresh samples */
uint16_t BNO055_SAMPLERATE_DELAY_MS = 10;

const int chipSelect = BUILTIN_SDCARD; // Change this if you have an external SD card module

//Functionality Settings
const int print = 0; //Change this to 1 to see live data printed to monitor
const int recordMeasurements = 1;

// Check I2C device address and correct line below (by default address is 0x29 or 0x28)
//                                   id, address
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28, &Wire1);

void setup(void)
{

  // Check if SD card is present
  if (!SD.begin(chipSelect)) {
    // Don't do anything more:
    return;
  }
  if (SD.exists("flightData.csv")) {
    SD.remove("flightData.csv");

  }
  File dataFile = SD.open("flightData.csv", FILE_WRITE);
  if (dataFile) {
    dataFile.println("milliseconds,orientationx,orientationy,orientationz,angVelocityx,angVelocityy,angVelocityz,linAccelerationx,linAccelerationy,linAccelerationz,magneticx,magneticy,magneticz,accelerationx,accelerationy,accelerationz,gravityx,gravityy,gravityz,altitude");
    dataFile.close();
  }
  /* Initialise the sensor */
  if (!bno.begin())
  {
    /* There was a problem detecting the BNO055 ... check your connections */
    while (1);
  }

  if (!bmp.begin_I2C(0x77, &Wire2)) {   // hardware I2C mode, can pass in address & alt Wire
  //if (! bmp.begin_SPI(BMP_CS)) {  // hardware SPI mode  
  //if (! bmp.begin_SPI(BMP_CS, BMP_SCK, BMP_MISO, BMP_MOSI)) {  // software SPI mode
    //Serial.println("Could not find a valid BMP3 sensor, check wiring!");
    while (1);
  }

  bmp.setTemperatureOversampling(BMP3_OVERSAMPLING_8X);
  bmp.setPressureOversampling(BMP3_OVERSAMPLING_4X);
  bmp.setIIRFilterCoeff(BMP3_IIR_FILTER_COEFF_3);
  bmp.setOutputDataRate(BMP3_ODR_50_HZ);

  delay(1000);
}

void loop(void)
{
  //could add VECTOR_ACCELEROMETER, VECTOR_MAGNETOMETER,VECTOR_GRAVITY...
  sensors_event_t orientationData , angVelocityData , linearAccelData, magnetometerData, accelerometerData, gravityData;
  bno.getEvent(&orientationData, Adafruit_BNO055::VECTOR_EULER);
  bno.getEvent(&angVelocityData, Adafruit_BNO055::VECTOR_GYROSCOPE);
  bno.getEvent(&linearAccelData, Adafruit_BNO055::VECTOR_LINEARACCEL);
  bno.getEvent(&magnetometerData, Adafruit_BNO055::VECTOR_MAGNETOMETER);
  bno.getEvent(&accelerometerData, Adafruit_BNO055::VECTOR_ACCELEROMETER);
  bno.getEvent(&gravityData, Adafruit_BNO055::VECTOR_GRAVITY);

  if (! bmp.performReading()) {
    //Serial.println("Failed to perform reading :(");
    return;
  }

if (recordMeasurements == 1){
  File dataFile = SD.open("flightData.csv", FILE_WRITE);
// Writing the timestamp
  dataFile.print(String(millis()) + ",");

  // Writing orientation data
  dataFile.print(String(orientationData.orientation.x) + ",");
  dataFile.print(String(orientationData.orientation.y) + ",");
  dataFile.print(String(orientationData.orientation.z) + ",");

  // Writing angular velocity data
  dataFile.print(String(angVelocityData.gyro.x) + ",");
  dataFile.print(String(angVelocityData.gyro.y) + ",");
  dataFile.print(String(angVelocityData.gyro.z) + ",");

  // Writing linear acceleration data
  dataFile.print(String(linearAccelData.acceleration.x) + ",");
  dataFile.print(String(linearAccelData.acceleration.y) + ",");
  dataFile.print(String(linearAccelData.acceleration.z) + ",");

  // Writing magnetometer data
  dataFile.print(String(magnetometerData.magnetic.x) + ",");
  dataFile.print(String(magnetometerData.magnetic.y) + ",");
  dataFile.print(String(magnetometerData.magnetic.z) + ",");

  // Writing accelerometer data
  dataFile.print(String(accelerometerData.acceleration.x) + ",");
  dataFile.print(String(accelerometerData.acceleration.y) + ",");
  dataFile.print(String(accelerometerData.acceleration.z) + ",");

 // Writing accelerometer data
  dataFile.print(String(gravityData.acceleration.x) + ",");
  dataFile.print(String(gravityData.acceleration.y) + ",");
  dataFile.print(String(gravityData.acceleration.z) + ",");

  dataFile.println(String(bmp.readAltitude(SEALEVELPRESSURE_HPA)));
  dataFile.close();
}
}


void printEvent(sensors_event_t* event) {
  double x = -1000000, y = -1000000 , z = -1000000; //dumb values, easy to spot problem
  if (event->type == SENSOR_TYPE_ACCELEROMETER) {
    x = event->acceleration.x;
    y = event->acceleration.y;
    z = event->acceleration.z;
  }
  else if (event->type == SENSOR_TYPE_ORIENTATION) {
    x = event->orientation.x;
    y = event->orientation.y;
    z = event->orientation.z;
  }
  else if (event->type == SENSOR_TYPE_MAGNETIC_FIELD) {
    x = event->magnetic.x;
    y = event->magnetic.y;
    z = event->magnetic.z;
  }
  else if (event->type == SENSOR_TYPE_GYROSCOPE) {
    x = event->gyro.x;
    y = event->gyro.y;
    z = event->gyro.z;
  }
  else if (event->type == SENSOR_TYPE_ROTATION_VECTOR) {
    x = event->gyro.x;
    y = event->gyro.y;
    z = event->gyro.z;
  }
  else if (event->type == SENSOR_TYPE_LINEAR_ACCELERATION) {
    x = event->acceleration.x;
    y = event->acceleration.y;
    z = event->acceleration.z;
  }
  else if (event->type == SENSOR_TYPE_GRAVITY) {
    x = event->acceleration.x;
    y = event->acceleration.y;
    z = event->acceleration.z;
  }
  else {
  }

}



