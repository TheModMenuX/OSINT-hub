import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

interface PortScan {
  port: number;
  open: boolean;
  service: string;
}

export function NetworkScanner() {
  const [target, setTarget] = useState('');
  const [results, setResults] = useState<PortScan[]>([]);
  const [scanning, setScanning] = useState(false);

  const handleScan = async () => {
    setScanning(true);
    try {
      const response = await fetch(`/api/scan?target=${target}`);
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Error:', error);
    }
    setScanning(false);
  };

  return (
    <Card className="w-full max-w-2xl mx-auto dark:bg-slate-800">
      <CardHeader>
        <CardTitle>Network Scanner</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex space-x-2 mb-4">
          <Input
            placeholder="Enter IP address or hostname"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
          />
          <Button onClick={handleScan} disabled={scanning}>
            {scanning ? 'Scanning...' : 'Scan'}
          </Button>
        </div>

        {results.length > 0 && (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Port</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Service</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {results.map((result) => (
                <TableRow key={result.port}>
                  <TableCell>{result.port}</TableCell>
                  <TableCell>
                    <span className={result.open ? 'text-green-500' : 'text-red-500'}>
                      {result.open ? 'Open' : 'Closed'}
                    </span>
                  </TableCell>
                  <TableCell>{result.service}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}