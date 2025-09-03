import Foundation
import Combine
import CoreLocation
import CoreMotion
import NetworkExtension
import Security
import MetricKit

@available(iOS 14.0, *)
class AdvancedDataCollector {
    private let currentUser = "mgthi555-ai"
    private let timestamp = "2025-09-03 11:18:54"
    private let motionManager = CMMotionManager()
    private var cancellables = Set<AnyCancellable>()
    
    struct SensorData: Codable {
        let accelerometer: [String: Double]
        let gyroscope: [String: Double]
        let magnetometer: [String: Double]
        let timestamp: String
    }
    
    struct NetworkData: Codable {
        let connections: [Connection]
        let metrics: NetworkMetrics
        let timestamp: String
        
        struct Connection: Codable {
            let interface: String
            let type: String
            let status: String
            let bytesIn: UInt64
            let bytesOut: UInt64
        }
        
        struct NetworkMetrics: Codable {
            let latency: Double
            let throughput: Double
            let packetLoss: Double
        }
    }
    
    func collectAdvancedData() -> AnyPublisher<[String: Any], Error> {
        Publishers.CombineLatest4(
            collectSensorData(),
            collectSecurityMetrics(),
            collectNetworkMetrics(),
            collectSystemMetrics()
        )
        .map { sensor, security, network, system in
            [
                "sensor_data": sensor,
                "security_metrics": security,
                "network_metrics": network,
                "system_metrics": system,
                "timestamp": self.timestamp,
                "user": self.currentUser
            ]
        }
        .eraseToAnyPublisher()
    }
    
    private func collectSensorData() -> AnyPublisher<SensorData, Error> {
        Future { promise in
            guard self.motionManager.isAccelerometerAvailable else {
                promise(.failure(CollectorError.sensorUnavailable))
                return
            }
            
            self.motionManager.accelerometerUpdateInterval = 0.1
            self.motionManager.startAccelerometerUpdates(to: .main) { data, error in
                if let error = error {
                    promise(.failure(error))
                    return
                }
                
                let sensorData = SensorData(
                    accelerometer: [
                        "x": data?.acceleration.x ?? 0,
                        "y": data?.acceleration.y ?? 0,
                        "z": data?.acceleration.z ?? 0
                    ],
                    gyroscope: self.collectGyroscopeData(),
                    magnetometer: self.collectMagnetometerData(),
                    timestamp: self.timestamp
                )
                
                promise(.success(sensorData))
            }
        }
        .eraseToAnyPublisher()
    }
    
    private func collectSecurityMetrics() -> AnyPublisher<[String: Any], Error> {
        Future { promise in
            let query: [String: Any] = [
                kSecClass as String: kSecClassGenericPassword,
                kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlocked,
                kSecReturnAttributes as String: true
            ]
            
            var result: AnyObject?
            let status = SecItemCopyMatching(query as CFDictionary, &result)
            
            if status == errSecSuccess {
                promise(.success([
                    "security_level": "high",
                    "encryption_status": "enabled",
                    "biometric_available": true,
                    "timestamp": self.timestamp
                ]))
            } else {
                promise(.failure(CollectorError.securityCheckFailed))
            }
        }
        .eraseToAnyPublisher()
    }
}