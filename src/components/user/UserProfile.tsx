import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

interface UserProfileProps {
  username: string;
  lastLogin: string;
  avatarUrl?: string;
}

export function UserProfile({ username, lastLogin, avatarUrl }: UserProfileProps) {
  return (
    <Card className="w-full max-w-md mx-auto dark:bg-slate-800">
      <CardHeader className="flex flex-row items-center space-x-4">
        <Avatar className="h-12 w-12">
          <AvatarImage src={avatarUrl} alt={username} />
          <AvatarFallback>{username.slice(0, 2).toUpperCase()}</AvatarFallback>
        </Avatar>
        <div>
          <CardTitle className="text-xl font-bold dark:text-white">
            {username}
          </CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="flex justify-between items-center dark:text-gray-200">
          <span>Last Login:</span>
          <span className="font-mono">{lastLogin}</span>
        </div>
      </CardContent>
    </Card>
  );
}