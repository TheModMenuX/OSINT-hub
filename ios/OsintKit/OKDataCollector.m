#import "OKDataCollector.h"
#import <CoreLocation/CoreLocation.h>
#import <NetworkExtension/NetworkExtension.h>
#import <Security/Security.h>

@interface OKDataCollector () <CLLocationManagerDelegate>

@property (nonatomic, strong) CLLocationManager *locationManager;
@property (nonatomic, strong) NSString *currentUser;
@property (nonatomic, strong) NSString *timestamp;
@property (nonatomic, strong) NSMutableDictionary *collectedData;

@end

@implementation OKDataCollector

- (instancetype)init {
    self = [super init];
    if (self) {
        _locationManager = [[CLLocationManager alloc] init];
        _locationManager.delegate = self;
        _currentUser = @"mgthi555-ai";
        _timestamp = @"2025-09-03 11:13:42";
        _collectedData = [NSMutableDictionary dictionary];
    }
    return self;
}

- (void)startDataCollection {
    [self.locationManager requestWhenInUseAuthorization];
    [self.locationManager startUpdatingLocation];
    [self collectNetworkData];
    [self collectDeviceData];
}

- (void)collectNetworkData {
    NEHotspotNetwork *currentNetwork = [NEHotspotNetwork fetchCurrentWithError:nil];
    
    NSDictionary *networkData = @{
        @"ssid": currentNetwork.SSID ?: @"",
        @"bssid": currentNetwork.BSSID ?: @"",
        @"security": @(currentNetwork.secure),
        @"signalStrength": @(currentNetwork.signalStrength),
        @"timestamp": self.timestamp,
        @"user": self.currentUser
    };
    
    [self.collectedData setObject:networkData forKey:@"network"];
}

- (void)collectDeviceData {
    UIDevice *device = [UIDevice currentDevice];
    
    NSDictionary *deviceData = @{
        @"name": device.name,
        @"model": device.model,
        @"systemVersion": device.systemVersion,
        @"identifierForVendor": device.identifierForVendor.UUIDString,
        @"batteryLevel": @(device.batteryLevel),
        @"timestamp": self.timestamp,
        @"user": self.currentUser
    };
    
    [self.collectedData setObject:deviceData forKey:@"device"];
}

#pragma mark - CLLocationManagerDelegate

- (void)locationManager:(CLLocationManager *)manager 
     didUpdateLocations:(NSArray<CLLocation *> *)locations {
    CLLocation *location = locations.lastObject;
    
    NSDictionary *locationData = @{
        @"latitude": @(location.coordinate.latitude),
        @"longitude": @(location.coordinate.longitude),
        @"altitude": @(location.altitude),
        @"speed": @(location.speed),
        @"timestamp": self.timestamp,
        @"user": self.currentUser
    };
    
    [self.collectedData setObject:locationData forKey:@"location"];
    [self.delegate dataCollector:self didCollectData:self.collectedData];
}

- (void)locationManager:(CLLocationManager *)manager 
       didFailWithError:(NSError *)error {
    NSLog(@"Location error: %@", error);
    [self.delegate dataCollector:self didFailWithError:error];
}

@end