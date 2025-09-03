import { UserProfile } from '../user/UserProfile';
import { DateTimeDisplay } from '../tools/DateTimeDisplay';

export function Header() {
  const currentTime = "2025-09-03 11:00:20";
  const currentUser = "mgthi555-ai";

  return (
    <header className="border-b dark:bg-slate-900 p-4">
      <div className="container mx-auto flex justify-between items-center">
        <nav className="space-x-4">
          <a href="/" className="hover:text-blue-500">Dashboard</a>
          <a href="/ide" className="hover:text-blue-500">Cloud IDE</a>
          <a href="/tools" className="hover:text-blue-500">OSINT Tools</a>
        </nav>
        
        <div className="flex items-center space-x-4">
          <DateTimeDisplay currentTime={currentTime} />
          <UserProfile username={currentUser} />
        </div>
      </div>
    </header>
  );
}