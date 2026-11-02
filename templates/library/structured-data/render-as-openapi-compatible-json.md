<!-- name: Render As OpenAPI-compatible JSON | category: structured-data | output: json -->
Take the text provided by the user and infer the appropriate JSON Schema that could validate an equivalent structured payload. Use OpenAPI 3.0 syntax with `type`, `properties`, and `required` fields. Only include fields present in the user's input.

Example Input:  
User: I need to meet John at 17:00 today at Paris Square.

Example Output:
```
{
  "type": "object",
  "properties": {
    "intent": { "type": "string" },
    "person": { "type": "string" },
    "time": { "type": "string", "format": "time" },
    "date": { "type": "string" },
    "location": { "type": "string" }
  },
  "required": ["person", "time", "date", "location"]
}
```
