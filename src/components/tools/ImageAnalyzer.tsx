import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Loader2 } from "lucide-react";

export function ImageAnalyzer() {
  const [file, setFile] = useState<File | null>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!file) return;

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('image', file);

      const response = await fetch('/api/analyze-image', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      setAnalysis(data);
    } catch (error) {
      console.error('Error:', error);
    }
    setLoading(false);
  };

  return (
    <Card className="w-full max-w-2xl mx-auto dark:bg-slate-800">
      <CardHeader>
        <CardTitle>Image Analyzer</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <Input
            type="file"
            accept="image/*"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
          
          <Button onClick={handleAnalyze} disabled={!file || loading}>
            {loading ? <Loader2 className="animate-spin mr-2" /> : null}
            Analyze Image
          </Button>

          {analysis && (
            <div className="mt-4 space-y-2 dark:text-gray-200">
              <h3 className="font-semibold">Results:</h3>
              <p>Dimensions: {analysis.dimensions.join(' x ')}</p>
              <p>Format: {analysis.format}</p>
              <p>Size: {(analysis.size_bytes / 1024).toFixed(2)} KB</p>
              
              <h4 className="font-semibold mt-4">Features:</h4>
              <ul className="list-disc pl-5">
                <li>Keypoints detected: {analysis.features.keypoints}</li>
                {analysis.features.dominant_colors?.map((color: any, index: number) => (
                  <li key={index}>Color {index + 1}: {color[0]} ({color[1]} pixels)</li>
                ))}
              </ul>
              
              <h4 className="font-semibold mt-4">Metadata:</h4>
              <ul className="list-disc pl-5">
                {Object.entries(analysis.metadata).map(([key, value]) => (
                  <li key={key}>{key}: {value as string}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}