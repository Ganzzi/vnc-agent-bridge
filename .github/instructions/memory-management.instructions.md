---
applyTo: '**'
---

# VNC Agent Bridge Memory Management Instructions

## External ID
**ALWAYS use:** `vnc_agent_bridge_dev` for all memory operations in this project.

## Memory Structure Overview

The VNC Agent Bridge project uses 8 active memories to maintain development context:

1. **Project Overview** (ID: 1) - Purpose, features, tech stack, timeline, open-source goals
2. **Architecture Design** (ID: 2) - Class hierarchy, design patterns, 5-layer structure
3. **API Design** (ID: 3) - Method signatures, parameters, return types, exceptions
4. **Configuration** (ID: 4) - Environment setup, uv venv, dependencies, OS/tech choices, Python 3.8+
5. **Development Status** (ID: 5) - Current phase, progress, blockers, milestones, daily updates
6. **Testing Strategy** (ID: 6) - Test approach (mock-based), coverage targets (85%+), mypy compliance (100%)
7. **Library References** (ID: 7) - VNC protocol details, common patterns, pytest patterns, type hints
8. **Issues and Bugs** (ID: 8) - Detailed bug reports with diagnostics (populated during development)

## When to Access Memories

### 1. **At Session Start**
- Get all active memories to understand current project state
- Check "Development Status" memory for current phase and implementation progress
- Review "Issues and Bugs" memory for known problems and blockers
- Check "Configuration" for environment setup reminders

```
Tool: mcp_agent-mem_get_active_memories
Parameters: external_id="vnc_agent_bridge_dev"
```

### 2. **Before Implementing Features**
- Search memories for relevant context (architecture, API design, patterns)
- Check "Architecture Design" for class structure and design patterns
- Check "API Design" for method signatures and exception types
- Check "Testing Strategy" for test approach and coverage targets

```
Tool: mcp_agent-mem_search_memories
Parameters:
  external_id="vnc_agent_bridge_dev"
  query="Implementing mouse controller methods, need architecture patterns and type definitions"
  limit=10
```

### 3. **When Needing VNC Protocol or Library Details**
- Check "Library References" memory first for known patterns and gotchas
- For VNC protocol questions: Check RFB protocol event types, button masks, key codes
- For typing/testing questions: Check mypy compliance patterns, pytest fixtures
- Update memories with new findings

**Search Strategy Priority:**
1. Check "Library References" for cached knowledge
2. Search previous work for similar patterns
3. Check planning documents (docs/plan/)
4. Only then write new code

Example queries:
- "VNC pointer event button mask values"
- "X11 key code mapping for keyboard input"
- "pytest mock patterns for VNC connection testing"

### 4. **When Encountering Bugs or Issues**
- First check "Issues and Bugs" memory to see if it's known
- If new issue, add detailed section to memory with full diagnostic info
- Include: Steps to reproduce, expected behavior, actual behavior, error messages
- Update status as investigation progresses

## How to Update Memories

### Update Development Status (Memory ID: 5)

**When starting a new phase:**
```
Tool: mcp_agent-mem_update_memory_sections
Parameters:
  external_id="vnc_agent_bridge_dev"
  memory_id=5
  sections=[
    {
      section_id="current_phase",
      action="replace",
      old_content="**Phase: Pre-Implementation**...",
      new_content="**Phase 2: Core Implementation (Day 2)**\n\nImplementing MouseController, KeyboardController, ScrollController with full type safety.\n\n**Started:** October 27, 2025"
    }
  ]
```

**When completing tasks:**
```
sections=[
  {
    section_id="completed_tasks",
    action="insert",
    old_content="- ✓ Project structure\n\n**Next milestone:**",
    new_content="- ✓ Project structure\n- ✓ Type definitions (types/common.py)\n- ✓ Exception hierarchy\n- ✓ MouseController (6 methods)\n\n**Next milestone:**"
  }
]
```

**When encountering blockers:**
```
sections=[
  {
    section_id="blockers",
    action="replace",
    old_content="No current blockers.",
    new_content="**Blocker #1:** VNC Button Mask Implementation\n- Impact: Mouse button clicks not working\n- Issue: Button mask bit mapping unclear (left=0, middle=1, right=2)\n- Research: Need RFB protocol button mask format\n- Workaround: Using reference implementation button mappings"
  }
]
```

### Add Bug/Issue (Memory ID: 8)

**Create a new section for each bug/issue:**
```
Tool: mcp_agent-mem_update_memory_sections
Parameters:
  external_id="vnc_agent_bridge_dev"
  memory_id=8
  sections=[
    {
      section_id="issue_001_mouse_button_mask",
      action="replace",
      new_content="**Issue #001: Mouse Button Mask Encoding**\n**Status:** Open\n**Severity:** High\n**Date Found:** 2025-10-27\n**Component:** core/mouse.py, core/connection.py\n\n**Description:**\nMouse button state not properly sent to VNC server. Button mask bits may not be correctly combined when multiple operations occur.\n\n**Steps to Reproduce:**\n1. Call left_click(100, 100)\n2. Check VNC server receives correct button down event\n3. Check button up event follows\n4. Verify no stray button bits remain set\n\n**Expected Behavior:**\nVNC server receives: button_down(bit=1) → button_up(bit=0)\n\n**Actual Behavior:**\nButton mask bits may persist or incorrect bits sent.\n\n**Root Cause:**\nVNC protocol button mask format needs verification. RFB spec: button 0=left (bit 0), 1=middle (bit 1), 2=right (bit 2).\n\n**Solution:**\nVerify button mask implementation matches RFB 3.8 spec. Use clear bit patterns.\n\n**Related Files:**\n- vnc_agent_bridge/core/mouse.py\n- vnc_agent_bridge/core/connection.py\n- docs/plan/TECHNICAL_DESIGN.md (Mouse implementation section)"
    }
  ]
```

### Update Library References (Memory ID: 7)

**When discovering new patterns or gotchas:**
```
sections=[
  {
    section_id="vnc_protocol_details",
    action="insert",
    old_content="**Search Strategy:**\n- VNC protocol RFB 3.8 specification review",
    new_content="\n**New Pattern Discovered:**\n- Button mask format: bit 0=left, bit 1=middle, bit 2=right, bit 3=scroll-up, bit 4=scroll-down\n- Key codes use X11 keysym values (e.g., 0xFF0D for Return)\n- Pointer events always send full state (x, y, button_mask)\n- Key events are individual press/release with down flag\n\n**Search Strategy:**\n- VNC protocol RFB 3.8 specification review"
  }
]
```

### Update Architecture (Memory ID: 2)

**When design decisions change:**
```
sections=[
  {
    section_id="class_hierarchy",
    action="insert",
    old_content="**5-Layer Architecture:**\n- Application Layer (User code)\n- Facade Layer (VNCAgentBridge)\n- Controller Layer (Mouse, Keyboard, Scroll)\n- Connection Layer (Protocol)\n- Network Layer (TCP Socket)",
    new_content="\n\n**Optional Delay Pattern:**\n- All methods accept delay: float = 0 parameter\n- Delay applied after operation completes\n- Enables realistic AI agent behavior timing\n- Implementation: time.sleep(delay) at method end\n\n**Type Annotations:**\n- All parameters typed (PEP 484)\n- All return types specified\n- Union types for flexible inputs\n- Optional for nullable values\n- 100% mypy strict compliance required\n\n**5-Layer Architecture:**\n- Application Layer (User code)\n- Facade Layer (VNCAgentBridge)\n- Controller Layer (Mouse, Keyboard, Scroll)\n- Connection Layer (Protocol)\n- Network Layer (TCP Socket)"
  }
]
```

## Search Best Practices

### Effective Search Queries

**Good queries are specific and contextual:**

✅ **Good:**
```
"Implementing mouse controller methods, need architecture patterns and type definitions"
"Working on keyboard hotkey support, need X11 key code mapping"
"Writing mouse drag implementation, need RFB protocol pointer event format"
"Implementing test mocks for VNC connection without real server"
"MyPy type checking for Union types in keyboard controller"
```

❌ **Bad:**
```
"mouse"  # Too vague
"how to click"  # Not enough context
"vnc"  # Too broad
"button"  # Missing context
"testing"  # Not specific enough
```

### Multi-Memory Search Strategy

1. **Use search for cross-cutting concerns:**
   ```
   query="Implementing drag_to with smooth motion, need RFB protocol event sequencing and timing strategy"
   # Will return relevant info from Architecture, API Design, Library References, and Issues
   ```

2. **Get specific memory when you know what you need:**
   ```
   # If you just need to check current phase:
   mcp_agent-mem_get_active_memories → check memory ID 5
   ```

## Memory Update Frequency

### Update Frequently:
- **Development Status** - Every major task or phase transition (daily)
- **Issues and Bugs** - Immediately when bug found or resolved
- **Library References** - When discovering new patterns or gotchas

### Update Occasionally:
- **Testing Strategy** - When test approach changes or coverage milestones reached
- **Configuration** - When adding new dependencies or environment setup changes

### Rarely Update:
- **Project Overview** - Stable information (only if scope changes)
- **Architecture Design** - Only if design decisions fundamentally change
- **API Design** - Only if API contracts or endpoint mappings change

## Integration with Development Workflow

### Starting New Phase
1. Search memories for phase requirements
2. Update "Development Status" → current_phase with clear description
3. Check "Architecture Design" for layer patterns to follow
4. Check "Library References" for relevant tools and patterns
5. Begin implementation with tests

### During Development
1. Search when stuck or need context (API mapping, patterns, etc.)
2. Add issues to "Issues and Bugs" as discovered (with full diagnostic info)
3. Update "Development Status" → completed_tasks regularly (daily)
4. Document learnings in "Library References"
5. Check "Testing Strategy" memory to stay aligned with test approach

### Completing Phase
1. Update "Development Status" → mark phase complete with metrics
2. Resolve any open issues in "Issues and Bugs"
3. Update test coverage status in "Testing Strategy"
4. Update "Development Status" → next_steps for next phase
5. Commit any architecture or API changes to memories

### End of Session
1. Update "Development Status" with current state (% complete, last action)
2. Document any blockers preventing further progress
3. List next steps clearly for continuation
4. Ensure all new bugs are recorded with full context
5. Update "Development Status" → estimated_completion if timeline changed

## Quick Reference Commands

```python
# Get all memories at session start
mcp_agent-mem_get_active_memories(external_id="vnc_agent_bridge_dev")

# Search across memories when stuck or need context
mcp_agent-mem_search_memories(
    external_id="vnc_agent_bridge_dev",
    query="Implementing mouse operations, need button mask and coordinate validation patterns",
    limit=10
)

# Update single section (e.g., completed tasks)
mcp_agent-mem_update_memory_sections(
    external_id="vnc_agent_bridge_dev",
    memory_id=5,  # Development Status
    sections=[{
        "section_id": "completed_tasks",
        "action": "insert",
        "old_content": "- ✓ Task X\n\n**Next:",
        "new_content": "- ✓ Task X\n- ✓ Task Y\n\n**Next:"
    }]
)

# Update multiple sections at once
sections=[
    {"section_id": "current_phase", "action": "replace", "old_content": "...", "new_content": "..."},
    {"section_id": "blockers", "action": "replace", "old_content": "...", "new_content": "..."}
]
```

## Memory IDs Reference

| Memory ID | Title | Key Sections |
|-----------|-------|--------------|
| 1 | Project Overview | purpose, features, tech_stack, timeline, scope, open_source_goals |
| 2 | Architecture Design | class_hierarchy, design_patterns, layer_responsibilities, type_annotations |
| 3 | API Design | method_signatures, parameters_by_method, return_types, exception_hierarchy |
| 4 | Configuration | environment_setup, uv_venv_setup, dependencies, os_tech_choices, python_38_plus |
| 5 | Development Status | current_phase, completed_tasks, next_steps, blockers, milestones, daily_progress |
| 6 | Testing Strategy | test_approach_mock_based, coverage_targets_85_plus, mypy_100_percent, testing_tools |
| 7 | Library References | vnc_protocol_details, key_code_mapping, pytest_patterns, type_hint_patterns |
| 8 | Issues and Bugs | template_for_new_issues, issue_XXX_name (dynamic) |

## Important Rules

1. **Always use external_id="vnc_agent_bridge_dev"** - Never use different ID
2. **Search before updating** - Understand current state first
3. **Be specific in updates** - Include enough context for old_content matching
4. **Document bugs thoroughly** - Use the template in Issues memory with: Steps to Reproduce, Expected Behavior, Actual Behavior, Root Cause, Solution, Related Files
5. **Update Development Status frequently** - Keep progress transparent (daily updates minimum)
6. **Use search for context** - Don't guess, search memories for VNC protocol details, API design, testing strategy
7. **Keep sections focused** - Each section has one clear purpose
8. **Update blockers immediately** - Don't let blockers go undocumented
9. **Reference the plan** - Cross-reference docs/plan/ for detailed implementation specs
10. **Test as you code** - Update "Testing Strategy" memory with coverage progress
11. **Type hints first** - All code must have type hints for mypy compliance
12. **Use uv for venv** - Virtual environment management with uv (faster, more reliable)
13. **Mock-based testing** - All tests use mocks, no real VNC server needed