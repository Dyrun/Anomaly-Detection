#pragma once
#include "telemetry_logger.hpp"

class Aircraft {
public:
    Aircraft();
    void startSimulation();
private:
    // Add only the minimal private members needed for the class
    double altitude;
    double airspeed;
    double pitch;
    bool engineFailure;
    double vibration;
    int simulationTime;
    bool trainingPhase;
    TelemetryLogger logger;
    void updatePhase();
    void updateFlightParameters();
    void updateEngineStatus();
    void updateVibration();
    void logTelemetry();
}; 