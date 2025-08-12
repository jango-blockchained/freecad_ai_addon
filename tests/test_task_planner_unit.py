from freecad_ai_addon.agent.task_planner import (
    ExecutionPlan,
    TaskPlanner,
    PlanStatus,
)
from freecad_ai_addon.agent.base_agent import (
    AgentTask,
    TaskType,
    TaskResult,
    TaskStatus,
)


def make_task(task_id: str) -> AgentTask:
    return AgentTask(
        id=task_id,
        task_type=TaskType.GEOMETRY_CREATION,
        description="noop",
        parameters={},
        context={},
    )


def test_execute_plan_completes_when_task_fails(monkeypatch):
    planner = TaskPlanner()
    plan = ExecutionPlan(id="p1")

    t1 = make_task("t1")
    t2 = make_task("t2")
    plan.add_task(t1)
    plan.add_task(t2, dependencies=["t1"])  # t2 depends on t1

    def fake_exec(self: TaskPlanner, task: AgentTask) -> TaskResult:
        if task.id == "t1":
            return TaskResult(status=TaskStatus.COMPLETED, result_data={"ok": True})
        return TaskResult(status=TaskStatus.FAILED, error_message="boom")

    monkeypatch.setattr(TaskPlanner, "_execute_single_task", fake_exec, raising=True)

    results = planner.execute_plan(plan)

    assert results["t1"].status == TaskStatus.COMPLETED
    assert results["t2"].status == TaskStatus.FAILED
    assert plan.status == PlanStatus.FAILED
    # Ensure the loop terminated (no hanging) by checking completed_at set
    assert plan.completed_at is not None


def test_execute_plan_all_success(monkeypatch):
    planner = TaskPlanner()
    plan = ExecutionPlan(id="p2")

    t1 = make_task("a")
    t2 = make_task("b")
    plan.add_task(t1)
    plan.add_task(t2, dependencies=["a"])  # sequential

    def fake_exec(_self: TaskPlanner, _task: AgentTask) -> TaskResult:
        return TaskResult(status=TaskStatus.COMPLETED, result_data={"ok": True})

    monkeypatch.setattr(TaskPlanner, "_execute_single_task", fake_exec, raising=True)

    results = planner.execute_plan(plan)

    assert results["a"].status == TaskStatus.COMPLETED
    assert results["b"].status == TaskStatus.COMPLETED
    assert plan.status == PlanStatus.COMPLETED
    assert plan.completed_at is not None
