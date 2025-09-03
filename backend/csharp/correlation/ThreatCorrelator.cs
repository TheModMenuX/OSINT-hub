using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.ML;
using Microsoft.ML.Data;
using System.Linq;
using Newtonsoft.Json;

namespace OSINT.ThreatCorrelation
{
    public class ThreatCorrelator
    {
        private readonly string _currentUser = "mgthi555-ai";
        private readonly string _timestamp = "2025-09-03 11:16:04";
        private readonly MLContext _mlContext;
        private readonly Dictionary<string, float> _threatWeights;
        
        public class ThreatEvent
        {
            [LoadColumn(0)]
            public string EventId { get; set; }
            
            [LoadColumn(1)]
            public string EventType { get; set; }
            
            [LoadColumn(2)]
            public string Source { get; set; }
            
            [LoadColumn(3)]
            public string Target { get; set; }
            
            [LoadColumn(4)]
            public float Severity { get; set; }
            
            [LoadColumn(5)]
            public string Timestamp { get; set; }
            
            [LoadColumn(6)]
            public string Metadata { get; set; }
        }
        
        public class CorrelationResult
        {
            public string CorrelationId { get; set; }
            public List<ThreatEvent> RelatedEvents { get; set; }
            public double ConfidenceScore { get; set; }
            public string AnalysisTimestamp { get; set; }
            public string AnalyzedBy { get; set; }
            public Dictionary<string, object> Insights { get; set; }
        }
        
        public ThreatCorrelator()
        {
            _mlContext = new MLContext(seed: 1);
            _threatWeights = InitializeThreatWeights();
        }
        
        private Dictionary<string, float> InitializeThreatWeights()
        {
            return new Dictionary<string, float>
            {
                {"MALWARE", 0.9f},
                {"NETWORK_ATTACK", 0.85f},
                {"DATA_LEAK", 0.8f},
                {"UNAUTHORIZED_ACCESS", 0.75f},
                {"SUSPICIOUS_BEHAVIOR", 0.6f}
            };
        }
        
        public async Task<CorrelationResult> CorrelateEvents(List<ThreatEvent> events)
        {
            var correlationId = Guid.NewGuid().ToString();
            var insights = new Dictionary<string, object>();
            
            // Temporal analysis
            var temporalPatterns = await AnalyzeTemporalPatterns(events);
            insights["temporal_patterns"] = temporalPatterns;
            
            // Source-target relationship analysis
            var relationships = AnalyzeRelationships(events);
            insights["relationship_graph"] = relationships;
            
            // Attack pattern recognition
            var attackPatterns = await RecognizeAttackPatterns(events);
            insights["attack_patterns"] = attackPatterns;
            
            // Calculate confidence score
            var confidenceScore = CalculateConfidenceScore(events, temporalPatterns, relationships);
            
            return new CorrelationResult
            {
                CorrelationId = correlationId,
                RelatedEvents = events,
                ConfidenceScore = confidenceScore,
                AnalysisTimestamp = _timestamp,
                AnalyzedBy = _currentUser,
                Insights = insights
            };
        }
        
        private async Task<Dictionary<string, object>> AnalyzeTemporalPatterns(List<ThreatEvent> events)
        {
            var patterns = new Dictionary<string, object>();
            
            // Group events by time windows
            var timeWindows = events
                .GroupBy(e => DateTime.Parse(e.Timestamp).ToString("yyyy-MM-dd HH:mm"))
                .OrderBy(g => g.Key)
                .ToDictionary(
                    g => g.Key,
                    g => g.ToList()
                );
            
            // Analyze event frequency
            patterns["event_frequency"] = timeWindows
                .ToDictionary(
                    kv => kv.Key,
                    kv => new
                    {
                        Count = kv.Value.Count,
                        Types = kv.Value
                            .GroupBy(e => e.EventType)
                            .Select(g => new { Type = g.Key, Count = g.Count() })
                    }
                );
            
            // Detect burst patterns
            patterns["burst_patterns"] = DetectBurstPatterns(timeWindows);
            
            return patterns;
        }
        
        private Dictionary<string, object> AnalyzeRelationships(List<ThreatEvent> events)
        {
            var relationships = new Dictionary<string, object>();
            
            // Build source-target graph
            var graph = events
                .GroupBy(e => (e.Source, e.Target))
                .ToDictionary(
                    g => g.Key,
                    g => new
                    {
                        EventCount = g.Count(),
                        TotalSeverity = g.Sum(e => e.Severity),
                        EventTypes = g.Select(e => e.EventType).Distinct()
                    }
                );
            
            // Identify central nodes
            var centralNodes = graph
                .GroupBy(kv => kv.Key.Source)
                .OrderByDescending(g => g.Count())
                .Take(5)
                .ToDictionary(
                    g => g.Key,
                    g => g.Count()
                );
            
            relationships["graph"] = graph;
            relationships["central_nodes"] = centralNodes;
            
            return relationships;
        }
        
        private async Task<List<object>> RecognizeAttackPatterns(List<ThreatEvent> events)
        {
            var patterns = new List<object>();
            
            // Train pattern recognition model
            var dataView = _mlContext.Data.LoadFromEnumerable(events);
            
            var pipeline = _mlContext.Transforms
                .Categorical()
                .OneHotEncoding("EventTypeEncoded", "EventType")
                .Append(_mlContext.Transforms.Concatenate("Features", "EventTypeEncoded", "Severity"))
                .Append(_mlContext.Clustering.Trainers.KMeans("Features", numberOfClusters: 5));
            
            var model = pipeline.Fit(dataView);
            
            // Predict clusters
            var predictions = model.Transform(dataView);
            var clusters = _mlContext.Data
                .CreateEnumerable<ClusterPrediction>(predictions, reuseRowObject: false)
                .ToList();
            
            // Analyze clusters for attack patterns
            var clusterAnalysis = clusters
                .GroupBy(p => p.PredictedClusterId)
                .Select(g => new
                {
                    ClusterId = g.Key,
                    EventCount = g.Count(),
                    AverageSeverity = g.Average(p => events[p.EventId].Severity),
                    DominantEventTypes = g
                        .GroupBy(p => events[p.EventId].EventType)
                        .OrderByDescending(eg => eg.Count())
                        .Take(3)
                        .Select(eg => new { Type = eg.Key, Count = eg.Count() })
                })
                .ToList();
            
            patterns.AddRange(clusterAnalysis);
            
            return patterns;
        }
        
        private class ClusterPrediction
        {
            [ColumnName("PredictedLabel")]
            public uint PredictedClusterId;
            
            [ColumnName("EventId")]
            public int EventId;
        }
        
        private double CalculateConfidenceScore(
            List<ThreatEvent> events,
            Dictionary<string, object> temporalPatterns,
            Dictionary<string, object> relationships)
        {
            double score = 0.0;
            
            // Event type weights
            score += events.Sum(e => _threatWeights.GetValueOrDefault(e.EventType, 0.5f));
            
            // Temporal density
            var eventDensity = temporalPatterns["event_frequency"] as Dictionary<string, object>;
            score += eventDensity?.Count * 0.1 ?? 0;
            
            // Relationship complexity
            var graph = relationships["graph"] as Dictionary<(string, string), object>;
            score += graph?.Count * 0.05 ?? 0;
            
            // Normalize score
            return Math.Min(score / (events.Count * 2.0), 1.0);
        }
    }
}