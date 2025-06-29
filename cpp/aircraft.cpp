#define _USE_MATH_DEFINES
#include "aircraft.hpp"
#include <cmath>
#include <thread>
#include <chrono>
#include <iostream>

Aircraft::Aircraft()
    : altitude(1000.0), airspeed(250.0), pitch(2.0), engineFailure(false), vibration(2.5), simulationTime(0), trainingPhase(true), logger("../telemetry.jsonl") {}

void Aircraft::startSimulation() {
    std::cout << "Starting Flight Telemetry Simulator..." << std::endl;
    while (true) {
        simulationTime++;
        updatePhase();
        updateFlightParameters();
        updateEngineStatus();
        updateVibration();
        logTelemetry();
        int delayMs = trainingPhase ? 0 : 500;
        if (delayMs > 0) {
            std::this_thread::sleep_for(std::chrono::milliseconds(delayMs));
        }
    }
}

void Aircraft::updatePhase() {
    if (simulationTime <= 120) {
        trainingPhase = true;
        engineFailure = false;
    } else {
        trainingPhase = false;
    }
}

void Aircraft::updateFlightParameters() {
    altitude += 10.0 * std::sin(pitch * M_PI / 180.0);
    if (engineFailure) {
        airspeed = 150.0 + 20.0 * std::sin(simulationTime % 5);
    } else {
        airspeed = 250.0 + 30.0 * std::cos(simulationTime % 8);
    }
    if (engineFailure) {
        pitch = 15.0 * std::sin(simulationTime % 3);
    } else {
        pitch = 2.0 + 5.0 * std::cos(simulationTime % 7);
    }
}

void Aircraft::updateEngineStatus() {
    if (!trainingPhase) {
        if (rand() % 20 == 0) engineFailure = true;
        if (rand() % 10 == 0) engineFailure = false;
    }
}

void Aircraft::updateVibration() {
    if (engineFailure) {
        vibration = 5.0 + static_cast<double>(rand()) / RAND_MAX * 5.0; // 5.0-10.0
    } else {
        vibration = 2.5 + static_cast<double>(rand()) / RAND_MAX; // 2.5-3.5
    }
}

void Aircraft::logTelemetry() {
    double timestamp = static_cast<double>(std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::system_clock::now().time_since_epoch()).count()) / 1000.0;
    logger.writeData(timestamp, altitude, airspeed, pitch, vibration, engineFailure, trainingPhase, simulationTime);
    std::cout << (trainingPhase ? "[TRAINING]" : "[TESTING]") << " Alt: " << altitude << "ft, Speed: " << airspeed << "kts, Pitch: " << pitch << "°, Vib: " << vibration << "g" << (engineFailure ? " [ENGINE FAILURE]" : "") << std::endl;
} 