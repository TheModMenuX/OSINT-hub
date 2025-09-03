package com.osinthub.timeline;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.stream.Collectors;

public class TimelineAnalyzer {
    private final String currentUser = "mgthi555-ai";
    private final String timestamp = "2025-09-03 11:16:04";
    private final Map<String, TimelineEvent> events;
    private final Map<String, List<TimelineEvent>> eventStreams;
    
    public class TimelineEvent {
        private String id;
        private String type;
        private Instant timestamp;
        private Map<String, Object> data;
        private List<String> relatedEvents;
        private double confidence;
        
        // Constructor and getters/setters
    }
    
    public class TimelineAnalysis {
        private List<TimelineEvent> events;
        private Map<String, List<TimelineEvent>> sequences;
        private Map<String, Double> patterns;
        private String analyzedBy;
        private String analysisTimestamp;
        
        public TimelineAnalysis() {
            this.analyzedBy = currentUser;
            this.analysisTimestamp = timestamp;
        }
    }
    
    public TimelineAnalyzer() {
        this.events = new HashMap<>();
        this.eventStreams = new HashMap<>();
    }
    
    public CompletableFuture<TimelineAnalysis> analyzeTimeline(List<TimelineEvent> events) {
        return CompletableFuture.supplyAsync(() -> {
            TimelineAnalysis analysis = new TimelineAnalysis();
            
            // Sort events chronologically
            List<TimelineEvent> sortedEvents = events.stream()
                .sorted(Comparator.comparing(TimelineEvent::getTimestamp))
                .collect(Collectors.toList());
            
            // Identify event sequences
            Map<String, List<TimelineEvent>> sequences = identifySequences(sortedEvents);
            analysis.sequences = sequences;
            
            // Detect patterns
            Map<String, Double> patterns = detectPatterns(sequences);
            analysis.patterns = patterns;
            
            // Find correlations
            findCorrelations(sortedEvents).forEach((key, value) -> {
                analysis.patterns.put("correlation_" + key, value);
            });
            
            return analysis;
        });
    }
    
    private Map<String, List<TimelineEvent>> identifySequences(List<TimelineEvent> events) {
        Map<String, List<TimelineEvent>> sequences = new HashMap<>();
        
        // Group events by type and temporal proximity
        for (int i = 0; i < events.size(); i++) {
            TimelineEvent current = events.get(i);
            List<TimelineEvent> sequence = new ArrayList<>();
            sequence.add(current);
            
            for (int j = i + 1; j < events.size(); j++) {
                TimelineEvent next = events.get(j);
                if (isRelatedEvent(current, next)) {
                    sequence.add(next);
                    i = j;
                } else {
                    break;
                }
            }
            
            if (sequence.size() > 1) {
                String sequenceId = UUID.randomUUID().toString();
                sequences.put(sequenceId, sequence);
            }
        }
        
        return sequences;
    }
    
    private boolean isRelatedEvent(TimelineEvent e1, TimelineEvent e2) {
        // Check temporal proximity
        long timeDiff = ChronoUnit.MINUTES.between(e1.timestamp, e2.timestamp);
        if (timeDiff > 30) return false;
        
        // Check type relationship
        if (e1.type.equals(e2.type)) return true;
        
        // Check data relationships
        return hasCommonAttributes(e1.data, e2.data);
    }
    
    private boolean hasCommonAttributes(Map<String, Object> data1, Map<String, Object> data2) {
        Set<String> commonKeys = new HashSet<>(data1.keySet());
        commonKeys.retainAll(data2.keySet());
        
        return commonKeys.stream()
            .anyMatch(key -> data1.get(key).equals(data2.get(key)));
    }
    
    private Map<String, Double> detectPatterns(Map<String, List<TimelineEvent>> sequences) {
        Map<String, Double> patterns = new HashMap<>();
        
        // Analyze sequence patterns
        sequences.forEach((id, sequence) -> {
            // Calculate sequence frequency
            double frequency = calculateSequenceFrequency(sequence);
            patterns.put("freq_" + id, frequency);
            
            // Calculate sequence consistency
            double consistency = calculateSequenceConsistency(sequence);
            patterns.put("cons_" + id, consistency);
            
            // Detect periodic patterns
            Optional<Double> periodicity = detectPeriodicity(sequence);
            periodicity.ifPresent(p -> patterns.put("period_" + id, p));
        });
        
        return patterns;
    }
    
    private double calculateSequenceFrequency(List<TimelineEvent> sequence) {
        long totalTime = ChronoUnit.SECONDS.between(
            sequence.get(0).timestamp,
            sequence.get(sequence.size() - 1).timestamp
        );
        
        return sequence.size() / (double) totalTime;
    }
    
    private double calculateSequenceConsistency(List<TimelineEvent> sequence) {
        if (sequence.size() < 2) return 1.0;
        
        List<Long> intervals = new ArrayList<>();
        for (int i = 1; i < sequence.size(); i++) {
            intervals.add(ChronoUnit.SECONDS.between(
                sequence.get(i-1).timestamp,
                sequence.get(i).timestamp
            ));
        }
        
        double mean = intervals.stream().mapToLong(i -> i).average().orElse(0);
        double variance = intervals.stream()
            .mapToDouble(i -> Math.pow(i - mean, 2))
            .average()
            .orElse(0);
            
        return 1.0 / (1.0 + Math.sqrt(variance));
    }
    
    private Optional<Double> detectPeriodicity(List<TimelineEvent> sequence) {
        if (sequence.size() < 3) return Optional.empty();
        
        // Calculate intervals between events
        List<Long> intervals = new ArrayList<>();
        for (int i = 1; i < sequence.size(); i++) {
            intervals.add(ChronoUnit.SECONDS.between(
                sequence.get(i-1).timestamp,
                sequence.get(i).timestamp
            ));
        }
        
        // Check for periodic patterns using autocorrelation
        double[] autocorrelation = calculateAutocorrelation(intervals);
        OptionalInt peakIndex = findPeakIndex(autocorrelation);
        
        return peakIndex.isPresent() 
            ? Optional.of((double) intervals.get(peakIndex.getAsInt()))
            : Optional.empty();
    }
}