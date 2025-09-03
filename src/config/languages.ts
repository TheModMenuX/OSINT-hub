export const languageConfigs = {
  typescript: {
    defaultContent: `// TypeScript Code
function hello(name: string): string {
    return \`Hello, \${name}!\`;
}`,
    extensions: ['.ts', '.tsx'],
    compiler: 'tsc'
  },
  python: {
    defaultContent: `# Python Code
def hello(name):
    return f"Hello, {name}!"`,
    extensions: ['.py'],
    interpreter: 'python3'
  },
  rust: {
    defaultContent: `// Rust Code
fn main() {
    println!("Hello, world!");
}`,
    extensions: ['.rs'],
    compiler: 'rustc'
  },
  cpp: {
    defaultContent: `// C++ Code
#include <iostream>

int main() {
    std::cout << "Hello, world!" << std::endl;
    return 0;
}`,
    extensions: ['.cpp', '.hpp'],
    compiler: 'g++'
  },
  julia: {
    defaultContent: `# Julia Code
function hello(name)
    println("Hello, \$name!")
end`,
    extensions: ['.jl'],
    interpreter: 'julia'
  }
};