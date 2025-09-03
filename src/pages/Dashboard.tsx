import { DateTimeDisplay } from '@/components/tools/DateTimeDisplay';
import { UserProfile } from '@/components/user/UserProfile';
import { OSINTToolsGrid } from '@/components/tools/OSINTToolsGrid';

export default function Dashboard() {
  const currentUser = {
    username: 'mgthi555-ai',
    lastLogin: '2025-09-03 10:46:53',
  };

  return (
    <div className="container mx-auto py-8 space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <UserProfile {...currentUser} />
        <DateTimeDisplay />
      </div>
      
      <section>
        <h2 className="text-2xl font-bold mb-6 dark:text-white">OSINT Tools</h2>
        <OSINTToolsGrid />
      </section>
    </div>
  );
}