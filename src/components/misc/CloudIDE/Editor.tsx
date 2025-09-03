import { useState, useEffect } from 'react';
import MonacoEditor from '@monaco-editor/react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { Terminal } from '@/components/ui/terminal';

const SUPPORTED_LANGUAGES = [
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'python', label: 'Python' },
  { value: 'rust', label: 'Rust' },
  { value: 'cpp', label: 'C++' },
  { value: 'julia', label: 'Julia' },
  { value: 'go', label: 'Go' }
];

export function CloudIDE() {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('typescript');
  const [output, setOutput] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  
  const handleRunCode = async () => {
    setIsRunning(true);
    try {
      const response = await fetch('/api/run-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language })
      });
      
      const data = await response.json();
      setOutput(data.output);
    } catch (error) {
      setOutput(`Error: ${error.message}`);
    }
    setIsRunning(false);
  };

  return (
    <div className="flex flex-col h-screen">
      <Card className="flex-1 dark:bg-slate-800">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Cloud IDE - Connected as mgthi555-ai</CardTitle>
          <div className="flex items-center space-x-2">
            <Select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              options={SUPPORTED_LANGUAGES}
            />
            <Button 
              onClick={handleRunCode}
              disabled={isRunning}
            >
              {isRunning ? 'Running...' : 'Run Code'}
            </Button>
          </div>
        </CardHeader>
        <CardContent className="h-full flex flex-col">
          <div className="flex-1">
            <MonacoEditor
              height="100%"
              language={language}
              value={code}
              onChange={(value) => setCode(value || '')}
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                wordWrap: 'on'
              }}
            />
          </div>
          <Terminal 
            className="h-48 mt-4"
            output={output}
            timestamp="2025-09-03 11:00:20"
          />
        </CardContent>
      </Card>
    </div>
  );
}