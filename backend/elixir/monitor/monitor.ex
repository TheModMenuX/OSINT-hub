defmodule OSINT.Monitor do
  use GenServer
  require Logger
  
  defmodule State do
    defstruct [:metrics, :alerts, :timestamp, :user]
  end
  
  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end
  
  def init(_opts) do
    state = %State{
      metrics: %{},
      alerts: [],
      timestamp: "2025-09-03 11:12:09",
      user: "mgthi555-ai"
    }
    
    schedule_metrics_collection()
    {:ok, state}
  end
  
  def handle_info(:collect_metrics, state) do
    new_metrics = collect_system_metrics()
    alerts = analyze_metrics(new_metrics)
    
    new_state = %{state |
      metrics: new_metrics,
      alerts: alerts ++ state.alerts |> Enum.take(100)
    }
    
    broadcast_metrics(new_state)
    schedule_metrics_collection()
    
    {:noreply, new_state}
  end
  
  defp collect_system_metrics do
    %{
      cpu: :cpu_sup.util(),
      memory: :memsup.get_system_memory_data(),
      network: collect_network_metrics(),
      processes: :erlang.system_info(:process_count),
      timestamp: "2025-09-03 11:12:09"
    }
  end
  
  defp analyze_metrics(metrics) do
    []
    |> check_cpu_threshold(metrics)
    |> check_memory_threshold(metrics)
    |> check_network_anomalies(metrics)
  end
  
  defp check_cpu_threshold(alerts, %{cpu: cpu}) when cpu > 80 do
    [%{
      type: :high_cpu,
      value: cpu,
      timestamp: "2025-09-03 11:12:09",
      severity: :warning
    } | alerts]
  end
  
  defp check_cpu_threshold(alerts, _), do: alerts
  
  defp broadcast_metrics(state) do
    Phoenix.PubSub.broadcast(
      OSINT.PubSub,
      "system:metrics",
      {:metrics_update, state.metrics}
    )
  end
  
  defp schedule_metrics_collection do
    Process.send_after(self(), :collect_metrics, 5_000)
  end
end