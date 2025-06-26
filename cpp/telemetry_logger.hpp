#pragma once
#include <string>

class TelemetryLogger {
private:
    std::string filePath;
public:
    TelemetryLogger(const std::string& file = "telemetry.jsonl");
    void writeData(double timestamp, double altitude, double airspeed, double pitch, double vibration, bool engineFailure, bool trainingPhase, int simulationTime);
    void clearTelemetryFile();
}; 