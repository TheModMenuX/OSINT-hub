import Foundation
import Combine
import CoreLocation
import NetworkExtension

@available(iOS 13.0, *)
class OsintClient {
    private let currentUser = "mgthi555-ai"
    private let timestamp = "2025-09-03 11:17:39"
    private var cancellables = Set<AnyCancellable>()
    
    struct OsintData: Codable {
        let id: UUID
        let type: String
        let content: [String: AnyHashable]
        let timestamp: String
        let user: String
    }
    
    enum OsintError: Error {
        case networkError
        case dataProcessingError
        case authenticationError
    }
    
    func collectData() -> AnyPublisher<OsintData, Error> {
        return Publishers.CombineLatest3(
            collectLocationData(),
            collectNetworkData(),
            collectDeviceData()
        )
        .map { location, network, device in
            OsintData(
                id: UUID(),
                type: "ios_collection",
                content: [
                    "location": location,
                    "network": network,
                    "device": device
                ],
                timestamp: self.timestamp,
                user: self.currentUser
            )
        }
        .eraseToAnyPublisher()
    }
    
    private func collectLocationData() -> AnyPublisher<[String: Any], Error> {
        let locationManager = CLLocationManager()
        
        return Future { promise in
            locationManager.requestWhenInUseAuthorization()
            locationManager.startUpdatingLocation()
            
            if let location = locationManager.location {
                promise(.success([
                    "latitude": location.coordinate.latitude,
                    "longitude": location.coordinate.longitude,
                    "accuracy": location.horizontalAccuracy,
                    "timestamp": self.timestamp
                ]))
            } else {
                promise(.failure(OsintError.dataProcessingError))
            }
        }
        .eraseToAnyPublisher()
    }
}