import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tool } from "@/types/tools";
import { Grid } from "@/components/ui/grid";

const osintTools: Tool[] = [
  {
    name: "Geolocation Tracker",
    description: "Track and monitor geographic locations in real-time",
    icon: "🌍",
    category: "Location",
    path: "/tools/geolocation"
  },
  {
    name: "Social Media Analyzer",
    description: "Analyze social media profiles and activities",
    icon: "📱",
    category: "Social",
    path: "/tools/social"
  },
  {
    name: "Network Scanner",
    description: "Scan and analyze network information",
    icon: "🔍",
    category: "Network",
    path: "/tools/network"
  },
  {
    name: "Image Analysis",
    description: "Extract metadata and analyze images",
    icon: "🖼️",
    category: "Media",
    path: "/tools/image"
  },
  // Add more tools here
];

export function OSINTToolsGrid() {
  return (
    <div className="container mx-auto py-8">
      <Grid className="gap-6" columns={{ sm: 1, md: 2, lg: 3 }}>
        {osintTools.map((tool) => (
          <Card key={tool.name} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="text-4xl mb-2">{tool.icon}</div>
              <CardTitle>{tool.name}</CardTitle>
              <CardDescription>{tool.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <span className="inline-block bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-100 text-xs px-2 py-1 rounded">
                {tool.category}
              </span>
            </CardContent>
          </Card>
        ))}
      </Grid>
    </div>
  );
}