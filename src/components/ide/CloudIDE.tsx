import { useState, useEffect } from 'react';
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import MonacoEditor from '@monaco-editor/react';

interface File {
  name: string;
  language: string;
  content: string;
}

export function CloudIDE() {
  const [files, setFiles] = useState<File[]>([]);
  const [currentFile, setCurrentFile] = useState<File | null>(null);
  const [theme, setTheme] = useState('vs-dark');
  
  const supportedLanguages = [
    { value: 'javascript', label: 'JavaScript' },
    { value: 'typescript', label: 'TypeScript' },
    { value: 'python', label: 'Python' },
    { value: 'rust', label: 'Rust' },
    { value: 'cpp', label: 'C++' },
    { value: 'julia', label: 'Julia' },
    { value: 'go', label: 'Go' }
  ];

  const handleFileCreate = () => {
    const newFile: File = {
      name: `untitled-${files.length + 1}`,
      language: 'typescript',
      content: ''
    };
    setFiles([...files, newFile]);
    setCurrentFile(newFile);
  };

  const handleFileSave = async () => {
    if (!currentFile) return;
    
    try {
      await fetch('/api/ide/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentFile)
      });
    } catch (error) {
      console.error('Error saving file:', error);
    }
  };

  return (
    <div className="h-screen flex flex-col">
      <div className="border-b p-4 flex items-center justify-between dark:bg-slate-900">
        <div className="flex items-center space-x-4">
          <Button onClick={handleFileCreate}>New File</Button>
          <Button onClick={handleFileSave}>Save</Button>
          <Select
            value={currentFile?.language || 'typescript'}
            onValueChange={(value) => {
              if (currentFile) {
                setCurrentFile({ ...currentFile, language: value });
              }
            }}
          >
            {supportedLanguages.map(lang => (
              <option key={lang.value} value={lang.value}>{lang.label}</option>
            ))}
          </Select>
        </div>
      </div>

      <div className="flex flex-1">
        <div className="w-64 border-r p-4 dark:bg-slate-800">
          {files.map(file => (
            <div
              key={file.name}
              className={`p-2 cursor-pointer rounded ${
                currentFile?.name === file.name ? 'bg-blue-500 text-white' : ''
              }`}
              onClick={() => setCurrentFile(file)}
            >
              {file.name}
            </div>
          ))}
        </div>

        <div className="flex-1">
          <MonacoEditor
            height="100%"
            language={currentFile?.language}
            value={currentFile?.content}
            theme={theme}
            onChange={(value) => {
              if (currentFile) {
                setCurrentFile({ ...currentFile, content: value || '' });
              }
            }}
            options={{
              minimap: { enabled: true },
              fontSize: 14,
              wordWrap: 'on',
              automaticLayout: true
            }}
          />
        </div>
      </div>
    </div>
  );
}