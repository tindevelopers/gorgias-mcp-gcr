# Ticket Assignment Guide

## ✅ Agent Assignment is Already Supported!

The MCP server **already supports** assigning tickets to agents. You don't need to add anything to the code - it's built-in functionality that needs to be used correctly.

## 📋 Available Tools

### 1. `create_ticket` - Create and Assign New Tickets

**Parameters:**
- `customer_id` (required) - ID of the customer
- `subject` (required) - Ticket subject
- `body` (required) - Ticket body content
- `assignee_id` (optional) - **ID of the agent to assign the ticket to**
- `priority` (optional) - Priority level: "low", "normal", "high", "urgent"

**Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "create_ticket",
    "arguments": {
      "customer_id": 625888921,
      "subject": "Customer inquiry",
      "body": "Customer needs help with order",
      "assignee_id": 65236828,
      "priority": "normal"
    }
  }
}
```

### 2. `update_ticket` - Assign or Reassign Existing Tickets

**Parameters:**
- `ticket_id` (required) - ID of the ticket to update
- `assignee_id` (optional) - **ID of the agent to assign/reassign the ticket to**
- `status` (optional) - Ticket status: "open", "closed", "pending", "solved"
- `priority` (optional) - Priority level
- `subject` (optional) - New subject

**Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "update_ticket",
    "arguments": {
      "ticket_id": 63355573,
      "assignee_id": 65236828,
      "status": "open"
    }
  }
}
```

## 🔍 How to Find Agent IDs

Agent IDs are integer values. You can find them by:

1. **From existing tickets** - Check the `assignee_user.id` field in ticket data
2. **From Gorgias dashboard** - Agent IDs are visible in the Gorgias admin interface
3. **From API** - Query the Gorgias `/users` endpoint (if you have access)

### Finding Agent ID from a Ticket

Use the `get_ticket` tool to see assignee information:

```bash
curl -X POST https://gorgias-mcp-server-880489367524.us-central1.run.app/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "get_ticket",
      "arguments": {"ticket_id": 63355573}
    }
  }'
```

Look for `assignee_user.id` in the response.

## 💡 Usage in Prompts/Instructions

When instructing the AI to create tickets, you can specify:

**Always assign new tickets to agent ID 65236828```

Or in tool calls:

```json
{
  "name": "create_ticket",
  "arguments": {
    "customer_id": 123,
    "subject": "Issue description",
    "body": "Detailed information",
    "assignee_id": 65236828,
    "priority": "normal"
  }
}
```

## ✅ Summary

- **Code already supports assignment** ✅
- **`create_ticket` accepts `assignee_id`** ✅
- **`update_ticket` accepts `assignee_id`** ✅
- **No code changes needed** ✅

You just need to:
1. Know the agent ID(s) you want to assign to
2. Include `assignee_id` in your tool calls
3. Add instructions to your prompt/system message to always include `assignee_id` when creating tickets


