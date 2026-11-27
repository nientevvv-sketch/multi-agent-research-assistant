
from src.workflow import build_workflow


def main():
    print("=" * 60)
    print("       MULTI-AGENT RESEARCH ASSISTANT")
    print("=" * 60)

    query = input("\nEnter your research question: ").strip()

    if not query:
        print("\nError: Research question cannot be empty.")
        return

    print("\nStarting research workflow...")
    print("Agents are working. Please wait.\n")

    try:
        workflow = build_workflow()

        initial_state = {
    	   "query": query,
    	   "plan": {},
    	   "research_material": "",
    	   "sources": [],
    	   "analysis": "",
    	   "fact_check": "",
    	   "final_report": ""
	}
        

        result = workflow.invoke(initial_state)

        print("\n" + "=" * 60)
        print("                 FINAL RESEARCH REPORT")
        print("=" * 60)
        print(result["final_report"])

    except Exception as error:
        print(f"\nWorkflow failed: {error}")


if __name__ == "__main__":
    main()
