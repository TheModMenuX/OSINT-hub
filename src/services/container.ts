import Docker from 'dockerode';
import { v4 as uuidv4 } from 'uuid';

const docker = new Docker();

interface ExecutionResult {
  success: boolean;
  output: string;
  error?: string;
}

export async function executeCode(code: string, language: string): Promise<ExecutionResult> {
  const containerId = uuidv4();
  const containerConfig = getContainerConfig(language, code);

  try {
    const container = await docker.createContainer({
      ...containerConfig,
      name: containerId,
    });

    await container.start();
    const output = await container.logs({ stdout: true, stderr: true });
    await container.remove({ force: true });

    return {
      success: true,
      output: output.toString()
    };
  } catch (error) {
    return {
      success: false,
      output: '',
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}

function getContainerConfig(language: string, code: string) {
  const configs = {
    python: {
      Image: 'python:3.9-slim',
      Cmd: ['python', '-c', code],
      WorkingDir: '/app',
    },
    rust: {
      Image: 'rust:1.68',
      Cmd: ['rustc', '-', '-o', '/tmp/out', '&&', '/tmp/out'],
      WorkingDir: '/app',
    },
    cpp: {
      Image: 'gcc:latest',
      Cmd: ['bash', '-c', `echo "${code}" > main.cpp && g++ main.cpp && ./a.out`],
      WorkingDir: '/app',
    },
    julia: {
      Image: 'julia:latest',
      Cmd: ['julia', '-e', code],
      WorkingDir: '/app',
    }
  };

  return configs[language as keyof typeof configs] || configs.python;
}