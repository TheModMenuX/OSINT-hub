import asyncnet, asyncdispatch, json, times, strutils
import std/[tables, sets, hashes]

type
  NetworkAnalyzer = ref object
    currentUser: string
    timestamp: string
    connections: TableRef[string, seq[Connection]]
    patterns: TableRef[string, Pattern]

  Connection = object
    source: string
    destination: string
    protocol: string
    timestamp: string
    metadata: JsonNode

  Pattern = object
    frequency: int
    lastSeen: string
    confidence: float
    metadata: JsonNode

proc newNetworkAnalyzer(): NetworkAnalyzer =
  result = NetworkAnalyzer(
    currentUser: "mgthi555-ai",
    timestamp: "2025-09-03 11:17:39",
    connections: newTable[string, seq[Connection]](),
    patterns: newTable[string, Pattern]()
  )

proc analyzeConnection(self: NetworkAnalyzer, conn: Connection) {.async.} =
  let patternKey = conn.source & "-" & conn.destination
  
  if not self.patterns.hasKey(patternKey):
    self.patterns[patternKey] = Pattern(
      frequency: 1,
      lastSeen: self.timestamp,
      confidence: 0.5,
      metadata: %*{"first_seen": self.timestamp}
    )
  else:
    inc self.patterns[patternKey].frequency
    self.patterns[patternKey].lastSeen = self.timestamp
    self.patterns[patternKey].confidence = min(
      1.0,
      self.patterns[patternKey].confidence + 0.1
    )