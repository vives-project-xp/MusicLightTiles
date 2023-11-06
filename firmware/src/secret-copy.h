// Define your secrets here:
#ifndef SECRETS_H
#define SECRETS_H

#include <Arduino.h>

const char* ssid = "";
const char* password = "";
const char* mqtt_server = "";
const int mqtt_port = 1883;
const char* mqtt_user = NULL; // Uses device_name if NULL
const char* mqtt_password = "";

#endif