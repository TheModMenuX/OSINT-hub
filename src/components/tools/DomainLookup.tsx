import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";

export function DomainLookup() {
  const [domain, setDomain] = useState('');
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleLookup = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/domain/${domain}`);
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Error:', error);
    }
    setLoading(false);
  };

  return (
    <Card className="w-full max-w-2xl mx-auto dark:bg-slate-800">
      <CardHeader>
        <CardTitle>Domain Lookup</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex space-x-2">
          <Input
            placeholder="Enter domain name"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
          />
          <Button onClick={handleLookup} disabled={loading}>
            {loading ? <Loader2 className="animate-spin" /> : 'Lookup'}
          </Button>
        </div>

        {results && (
          <div className="mt-4 space-y-2 dark:text-gray-200">
            <p><strong>Registrar:</strong> {results.registrar}</p>
            <p><strong>Created:</strong> {new Date(results.creation_date).toLocaleString()}</p>
            <p><strong>Expires:</strong> {new Date(results.expiration_date).toLocaleString()}</p>
            <p><strong>Nameservers:</strong></p>
            <ul className="list-disc pl-5">
              {results.nameservers.map((ns: string) => (
                <li key={ns}>{ns}</li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}