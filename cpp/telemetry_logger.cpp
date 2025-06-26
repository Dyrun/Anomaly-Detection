#include "telemetry_logger.hpp"
#include <fstream>
#include <iostream>
#include "json.hpp"

TelemetryLogger::TelemetryLogger(const std::string& file) {
    filePath = file;
    
    // Clear the telemetry file at startup
    clearTelemetryFile();
    std::cout << "Telemetry Logger initialized. Data file cleared at startup." << std::endl;
}

void TelemetryLogger::writeData(double timestamp, double altitude, double airspeed, double pitch, double vibration, bool engineFailure, bool trainingPhase, int simulationTime) {
    nlohmann::json data = {
        {"timestamp", timestamp},
        {"altitude", altitude},
        {"airspeed", airspeed},
        {"pitch", pitch},
        {"vibration", vibration},
        {"engineFailure", engineFailure},
        {"trainingPhase", trainingPhase},
        {"simulationTime", simulationTime}
    };
    std::ofstream out(filePath, std::ios::app);
    out << data.dump() << std::endl;
}

void TelemetryLogger::clearTelemetryFile() {
    // Open the file in truncate mode to clear its contents
    std::ofstream out(filePath, std::ios::trunc);
    out.close();
    std::cout << "Telemetry file cleared: " << filePath << std::endl;
} 