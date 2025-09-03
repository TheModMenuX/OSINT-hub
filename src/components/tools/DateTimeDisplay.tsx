import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function DateTimeDisplay() {
  const [currentTime, setCurrentTime] = useState({
    utc: '',
    local: ''
  });

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      
      setCurrentTime({
        utc: now.toISOString().replace('T', ' ').substring(0, 19),
        local: now.toLocaleString('en-US', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false
        })
      });
    };

    updateTime();
    const timer = setInterval(updateTime, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <Card className="w-full max-w-md mx-auto dark:bg-slate-800">
      <CardHeader>
        <CardTitle className="text-xl font-bold dark:text-white">Current Time</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex justify-between items-center dark:text-gray-200">
          <span>UTC:</span>
          <span className="font-mono">{currentTime.utc}</span>
        </div>
        <div className="flex justify-between items-center dark:text-gray-200">
          <span>Local:</span>
          <span className="font-mono">{currentTime.local}</span>
        </div>
      </CardContent>
    </Card>
  );
}