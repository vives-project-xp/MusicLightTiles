#ifndef SECRETS_H
#define SECRETS_H

#include <Arduino.h>

// Secrets
const char* ssid = "";
const char* password = "";
const char* mqtt_server = "";
const int mqtt_port = 1883;
const char* mqtt_user = NULL; // Uses device mac address as username if NULL
const char* mqtt_password = "";

// Configuration
const char* root_topic = "";

#endif