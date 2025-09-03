import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface Location {
  latitude: number;
  longitude: number;
  accuracy: number;
  timestamp: number;
}

export function GeolocationTracker() {
  const [location, setLocation] = useState<Location | null>(null);
  const [error, setError] = useState<string>('');
  const [isTracking, setIsTracking] = useState(false);

  const startTracking = () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser');
      return;
    }

    setIsTracking(true);
    setError('');

    navigator.geolocation.watchPosition(
      (position) => {
        setLocation({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          timestamp: position.timestamp
        });
      },
      (err) => {
        setError(`Error: ${err.message}`);
        setIsTracking(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 5000,
        maximumAge: 0
      }
    );
  };

  const stopTracking = () => {
    setIsTracking(false);
    setLocation(null);
  };

  return (
    <Card className="w-full max-w-md mx-auto dark:bg-slate-800">
      <CardContent className="p-6">
        <div className="space-y-4">
          <h2 className="text-2xl font-bold dark:text-white">Location Tracker</h2>
          
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {location && (
            <div className="space-y-2 dark:text-gray-200">
              <p>Latitude: {location.latitude}</p>
              <p>Longitude: {location.longitude}</p>
              <p>Accuracy: {location.accuracy}m</p>
              <p>Last Updated: {new Date(location.timestamp).toLocaleString()}</p>
            </div>
          )}

          <Button 
            onClick={isTracking ? stopTracking : startTracking}
            variant={isTracking ? "destructive" : "default"}
          >
            {isTracking ? 'Stop Tracking' : 'Start Tracking'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}