import json
from agent_graph.graph import GraphExecutor

if __name__ == "__main__":
    executor = GraphExecutor()

    with open("unstructured_data.json", "r") as file:
        input_json = json.load(file)

    executor.state["input_json"] = json.dumps(input_json)

    executor.execute()

    print("\n🔹 Generated JSON Schema:")
    print(json.dumps(executor.state.get("json_schema", {}), indent=4))

    print("\n🔹 Structured JSON Data:")
    structured_data = executor.state.get("structured_data")

    if structured_data:
        with open("app/structured_output.json", "w") as f:
            json.dump(structured_data, f, indent=4)

        print("\n✅ Structured JSON saved to `app/structured_output.json`")
        print(json.dumps(structured_data, indent=4))
    else:
        print("❌ ERROR: No structured data generated.")
