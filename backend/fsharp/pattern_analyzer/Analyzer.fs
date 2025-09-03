module OSINT.PatternAnalyzer

open System
open Microsoft.ML
open Microsoft.ML.Data
open Microsoft.ML.Transforms
open FSharp.Stats
open FSharp.Control

type PatternData = {
    Timestamp: string
    User: string
    Pattern: float[]
    Label: string
}

type PredictionResult = {
    Label: string
    Score: float
    Confidence: float
    Timestamp: string
    User: string
}

type NeuralAnalyzer() =
    let context = new MLContext(seed = Nullable 1)
    let timestamp = "2025-09-03 11:13:42"
    let currentUser = "mgthi555-ai"
    
    let pipeline =
        EstimatorChain()
            .Append(context.Transforms.Conversion.MapValueToKey("Label"))
            .Append(context.Transforms.Concatenate("Features", "Pattern"))
            .Append(context.Transforms.NormalizeMinMax("Features"))
            .Append(context.MulticlassClassification.Trainers.LbfgsMaximumEntropy())
            .Append(context.Transforms.Conversion.MapKeyToValue("PredictedLabel"))
    
    member _.TrainModel(data: PatternData seq) =
        let trainingData = 
            context.Data.LoadFromEnumerable(data)
        
        let model = pipeline.Fit(trainingData)
        
        // Save model for later use
        context.Model.Save(model, trainingData.Schema, "pattern_model.zip")
        model
    
    member _.AnalyzePattern(pattern: float[]) =
        let model = context.Model.Load("pattern_model.zip")
        let predictionEngine = 
            context.Model.CreatePredictionEngine<PatternData, PredictionResult>(model)
        
        let prediction = 
            predictionEngine.Predict(
                { Timestamp = timestamp
                  User = currentUser
                  Pattern = pattern
                  Label = "" })
        
        { prediction with 
            Timestamp = timestamp
            User = currentUser }
    
    member _.DetectAnomalies(patterns: float[] seq) =
        let matrix = DenseMatrix.ofColumns patterns
        let svd = matrix.Svd()
        
        // Use singular values to detect anomalies
        let threshold = svd.S |> Vector.sum |> (*) 0.01
        
        patterns
        |> Seq.mapi (fun i pattern ->
            let reconstruction = 
                svd.U.Column(0) 
                |> Vector.map (fun x -> x * svd.S.[0])
            
            let error = 
                Vector.distance (DenseVector.ofArray pattern) reconstruction
            
            { Timestamp = timestamp
              User = currentUser
              Pattern = pattern
              Label = if error > threshold then "anomaly" else "normal" })