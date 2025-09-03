import akka.actor.{Actor, ActorSystem, Props}
import akka.cluster.Cluster
import akka.cluster.ClusterEvent._
import scala.concurrent.Future
import scala.concurrent.duration._

object DistributedEngine {
  sealed trait ComputeMessage
  case class ComputeTask(code: String, language: String) extends ComputeMessage
  case class ComputeResult(result: String, timestamp: String) extends ComputeMessage
  
  class ComputeNode extends Actor {
    val cluster = Cluster(context.system)
    
    override def preStart(): Unit = {
      cluster.subscribe(self, classOf[MemberEvent], classOf[UnreachableMember])
    }
    
    def receive = {
      case task: ComputeTask =>
        val result = executeComputation(task)
        sender() ! ComputeResult(result, "2025-09-03 11:12:09")
        
      case state: CurrentClusterState =>
        log.info(s"Current cluster state: $state")
      
      case MemberUp(member) =>
        log.info(s"Member up: ${member.address}")
        
      case UnreachableMember(member) =>
        log.warning(s"Member unreachable: ${member.address}")
    }
    
    private def executeComputation(task: ComputeTask): String = {
      task.language match {
        case "scala" => ScalaExecutor.execute(task.code)
        case "java" => JavaExecutor.execute(task.code)
        case "kotlin" => KotlinExecutor.execute(task.code)
        case _ => s"Unsupported language: ${task.language}"
      }
    }
  }
}