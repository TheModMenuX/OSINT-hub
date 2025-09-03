package com.osinthub.ml

import groovy.transform.CompileStatic
import org.apache.spark.ml.Pipeline
import org.apache.spark.ml.classification.RandomForestClassifier
import org.apache.spark.ml.feature.*
import org.apache.spark.sql.Dataset
import org.apache.spark.sql.Row
import org.apache.spark.sql.SparkSession

@CompileStatic
class OsintMLPipeline {
    final String currentUser = 'mgthi555-ai'
    final String timestamp = '2025-09-03 11:18:54'
    
    private SparkSession spark
    private Pipeline pipeline
    
    OsintMLPipeline() {
        initializeSpark()
        buildPipeline()
    }
    
    private void initializeSpark() {
        spark = SparkSession.builder()
            .appName("OSINT-ML-Pipeline")
            .config("spark.master", "local[*]")
            .getOrCreate()
    }
    
    private void buildPipeline() {
        def tokenizer = new Tokenizer()
            .setInputCol("text")
            .setOutputCol("words")
            
        def hashingTF = new HashingTF()
            .setInputCol("words")
            .setOutputCol("features")
            .setNumFeatures(1000)
            
        def rf = new RandomForestClassifier()
            .setLabelCol("label")
            .setFeaturesCol("features")
            .setNumTrees(100)
            
        pipeline = new Pipeline()
            .setStages([tokenizer, hashingTF, rf] as PipelineStage[])
    }
    
    Dataset<Row> processData(Dataset<Row> data) {
        def model = pipeline.fit(data)
        def predictions = model.transform(data)
        
        predictions.withColumn("processed_at", lit(timestamp))
            .withColumn("processed_by", lit(currentUser))
    }
    
    Map analyzePredictions(Dataset<Row> predictions) {
        def metrics = calculateMetrics(predictions)
        def patterns = detectPatterns(predictions)
        def anomalies = findAnomalies(predictions)
        
        [
            metrics: metrics,
            patterns: patterns,
            anomalies: anomalies,
            timestamp: timestamp,
            user: currentUser
        ]
    }
    
    private Map calculateMetrics(Dataset<Row> predictions) {
        def evaluator = new MulticlassClassificationEvaluator()
            .setLabelCol("label")
            .setPredictionCol("prediction")
            
        [
            accuracy: evaluator.setMetricName("accuracy").evaluate(predictions),
            f1: evaluator.setMetricName("f1").evaluate(predictions),
            precision: evaluator.setMetricName("precision").evaluate(predictions),
            recall: evaluator.setMetricName("recall").evaluate(predictions)
        ]
    }
}