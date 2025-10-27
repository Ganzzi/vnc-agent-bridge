#!/usr/bin/env python3
"""
AI Agent Example
================

Demonstrates how an AI agent could use VNC Agent Bridge to:
    1. Perceive the screen state
    2. Plan actions
    3. Execute operations
    4. Verify results

This is a conceptual example showing the agent workflow pattern.

Requirements:
    - vnc-agent-bridge installed
    - VNC server running
"""

from vnc_agent_bridge import VNCAgentBridge, VNCException
import time


class SimpleAIAgent:
    """Conceptual AI Agent for VNC interaction."""

    def __init__(self, host: str = "localhost", port: int = 5900):
        """Initialize the AI agent."""
        self.vnc = VNCAgentBridge(host, port=port)
        self.action_log: list[str] = []

    def __enter__(self) -> "SimpleAIAgent":
        """Context manager entry."""
        self.vnc.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.vnc.disconnect()

    def log_action(self, action: str) -> None:
        """Log an action taken."""
        self.action_log.append(action)
        print(f"  [Action] {action}")

    def perceive(self) -> dict:
        """Perceive the current screen state."""
        # In a real agent, this would analyze screen capture
        # For now, just track mouse position
        x, y = self.vnc.mouse.get_position()
        state = {
            "mouse_x": x,
            "mouse_y": y,
            "timestamp": time.time(),
        }
        print(f"[Perception] Mouse at ({x}, {y})")
        return state

    def plan(self, goal: str) -> list[str]:
        """Plan actions to achieve goal."""
        # Simplified planning - in reality this would use AI
        plan = {
            "click_button": ["move_to_button", "click"],
            "type_text": ["click_input_field", "clear_field", "type"],
            "submit_form": ["move_to_submit", "click", "wait"],
            "scroll_page": ["scroll_down"],
        }
        actions = plan.get(goal, [])
        print(f"[Planning] Goal: {goal}")
        print(f"  Plan: {' -> '.join(actions)}")
        return actions

    def execute_action(self, action: str, params: dict = None) -> None:
        """Execute a single action."""
        params = params or {}

        if action == "move_to_button":
            # Example: move to approximate button location
            self.vnc.mouse.move_to(300, 400, delay=0.2)
            self.log_action(f"Moved to button at (300, 400)")

        elif action == "click":
            self.vnc.mouse.left_click(delay=0.2)
            self.log_action("Clicked")

        elif action == "click_input_field":
            x, y = params.get("coords", (100, 100))
            self.vnc.mouse.left_click(x, y, delay=0.2)
            self.log_action(f"Clicked input field at ({x}, {y})")

        elif action == "clear_field":
            # Select all and delete
            self.vnc.keyboard.hotkey("ctrl", "a", delay=0.1)
            self.vnc.keyboard.press_key("delete", delay=0.1)
            self.log_action("Cleared field")

        elif action == "type":
            text = params.get("text", "")
            self.vnc.keyboard.type_text(text, delay=0.05)
            self.log_action(f"Typed: {text}")

        elif action == "move_to_submit":
            self.vnc.mouse.move_to(400, 500, delay=0.2)
            self.log_action("Moved to submit button")

        elif action == "wait":
            delay = params.get("delay", 1.0)
            time.sleep(delay)
            self.log_action(f"Waited {delay}s")

        elif action == "scroll_down":
            amount = params.get("amount", 5)
            self.vnc.scroll.scroll_down(amount=amount, delay=0.3)
            self.log_action(f"Scrolled down {amount} ticks")

    def execute_plan(self, plan: list[str], params: dict = None) -> None:
        """Execute a sequence of actions."""
        params = params or {}
        for action in plan:
            self.execute_action(action, params)

    def verify_result(self, expected_state: str) -> bool:
        """Verify that the action succeeded."""
        # In a real agent, this would analyze screen capture
        # For now, just check if we're still connected
        state = self.perceive()
        success = state is not None
        print(
            f"[Verification] Expected state: {expected_state} - {'✓' if success else '✗'}"
        )
        return success


def example_1_simple_click_task():
    """Example: Agent performs a simple click task."""
    print("\n" + "=" * 50)
    print("Example 1: Simple Click Task")
    print("=" * 50)

    try:
        with SimpleAIAgent("localhost", port=5900) as agent:
            print("\n[Task] Click the submit button")
            print("-" * 50)

            # Step 1: Perceive current state
            agent.perceive()

            # Step 2: Plan actions
            plan = agent.plan("click_button")

            # Step 3: Execute plan
            agent.execute_plan(plan)

            # Step 4: Verify result
            agent.verify_result("button_clicked")

    except VNCException as e:
        print(f"✗ Agent error: {e}")


def example_2_form_filling_task():
    """Example: Agent fills out a form."""
    print("\n" + "=" * 50)
    print("Example 2: Form Filling Task")
    print("=" * 50)

    try:
        with SimpleAIAgent("localhost", port=5900) as agent:
            print("\n[Task] Fill out a form with user data")
            print("-" * 50)

            # Step 1: Perceive
            agent.perceive()

            # Step 2: Plan - fill form
            plan = agent.plan("type_text")

            # Step 3: Execute - with form-specific parameters
            steps = [
                ("click_input_field", {"coords": (100, 100)}),
                ("clear_field", {}),
                ("type", {"text": "John Doe"}),
                ("wait", {"delay": 0.5}),
                ("move_to_button", {}),
                ("click", {}),
            ]

            print("\n[Executing form fill sequence]")
            for action, params in steps:
                agent.execute_action(action, params)

            # Step 4: Verify
            agent.verify_result("form_filled")

    except VNCException as e:
        print(f"✗ Agent error: {e}")


def example_3_scroll_and_click_task():
    """Example: Agent scrolls and clicks."""
    print("\n" + "=" * 50)
    print("Example 3: Scroll and Click Task")
    print("=" * 50)

    try:
        with SimpleAIAgent("localhost", port=5900) as agent:
            print("\n[Task] Scroll down and click a link")
            print("-" * 50)

            # Step 1: Perceive
            agent.perceive()

            # Step 2: Execute scroll sequence
            print("\n[Executing scroll and click]")
            steps = [
                ("scroll_down", {"amount": 5}),
                ("wait", {"delay": 0.5}),
                ("move_to_button", {}),
                ("click", {}),
            ]

            for action, params in steps:
                agent.execute_action(action, params)

            # Step 3: Verify
            agent.verify_result("link_clicked")

    except VNCException as e:
        print(f"✗ Agent error: {e}")


def example_4_multi_step_workflow():
    """Example: Agent executes complex multi-step workflow."""
    print("\n" + "=" * 50)
    print("Example 4: Multi-Step Workflow")
    print("=" * 50)

    try:
        with SimpleAIAgent("localhost", port=5900) as agent:
            print("\n[Task] Execute complex workflow:")
            print("  1. Find and click search box")
            print("  2. Type search query")
            print("  3. Press Enter")
            print("  4. Wait for results")
            print("  5. Click first result")
            print("-" * 50)

            # Step 1: Initial perception
            agent.perceive()

            # Step 2: Workflow steps
            workflow = [
                ("click_input_field", {"coords": (200, 50)}),  # Search box
                ("clear_field", {}),
                ("type", {"text": "AI agent VNC control"}),
                ("wait", {"delay": 0.3}),
                ("press_return", {}),  # Would need custom impl
                ("wait", {"delay": 1.0}),  # Wait for results
                ("move_to_button", {}),
                ("click", {}),  # Click first result
            ]

            print("\n[Executing workflow]")
            for action, params in workflow[:-2]:  # Skip custom actions
                agent.execute_action(action, params)

            # Step 3: Final verification
            agent.verify_result("workflow_complete")

            # Print action log
            print("\n[Action Log]")
            for i, action in enumerate(agent.action_log, 1):
                print(f"  {i}. {action}")

    except VNCException as e:
        print(f"✗ Agent error: {e}")


def example_5_agent_reasoning():
    """Example: Demonstrate agent reasoning and planning."""
    print("\n" + "=" * 50)
    print("Example 5: Agent Reasoning")
    print("=" * 50)

    goals_and_plans = [
        ("click_button", ["move_to_button", "click"]),
        ("type_text", ["click_input_field", "clear_field", "type"]),
        ("submit_form", ["move_to_submit", "click", "wait"]),
        ("scroll_page", ["scroll_down"]),
    ]

    print("\n[Goal-to-Plan Mapping]")
    for goal, plan in goals_and_plans:
        print(f"\nGoal: {goal}")
        print(f"  Plan: {' -> '.join(plan)}")

    print("\n✓ Agent reasoning patterns demonstrated")


def example_6_error_recovery():
    """Example: Agent handles errors gracefully."""
    print("\n" + "=" * 50)
    print("Example 6: Error Recovery")
    print("=" * 50)

    print("\n[Agent Error Recovery]")

    try:
        with SimpleAIAgent("localhost", port=5900) as agent:
            # This should fail, but agent handles it
            print("\nAttempt 1: Click at invalid coordinates")
            try:
                agent.vnc.mouse.left_click(-1, 100)
            except Exception as e:
                print(f"  ✓ Caught error: {type(e).__name__}")
                print(f"  ✓ Recovery: Trying alternative approach")

            # Recovery attempt
            print("Attempt 2: Click at valid coordinates")
            agent.vnc.mouse.left_click(100, 100)
            print(f"  ✓ Success with fallback coordinates")

    except VNCException as e:
        print(f"Agent error: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("VNC Agent Bridge - AI Agent Examples")
    print("=" * 50)

    print("\nThese examples demonstrate how an AI agent could use")
    print("VNC Agent Bridge to interact with remote systems.")
    print("\nAgent Workflow:")
    print("  1. Perceive: Get current screen state")
    print("  2. Plan: Determine actions needed")
    print("  3. Execute: Perform the actions")
    print("  4. Verify: Check if goal was achieved")

    # Uncomment to run examples with real VNC server:
    # example_1_simple_click_task()
    # example_2_form_filling_task()
    # example_3_scroll_and_click_task()
    # example_4_multi_step_workflow()

    # These don't require VNC connection:
    example_5_agent_reasoning()
    example_6_error_recovery()

    print("\n" + "=" * 50)
    print("AI Agent examples completed!")
    print("Uncomment examples 1-4 to run with real VNC server")
    print("=" * 50)
