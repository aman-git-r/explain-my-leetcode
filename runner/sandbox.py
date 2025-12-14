import subprocess
import tempfile
import sys
import os
import json

TIME_LIMIT_SECONDS = 2


def run_user_code(user_code: str, test_cases: list, method_name: str):

    # 1. Create a temporary Python file
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False
    ) as temp_file:
        file_path = temp_file.name
        # --- Write user code ---
        temp_file.write(user_code)
        temp_file.write("\n\n")

        # --- Controlled execution wrapper ---
        temp_file.write("import json\n")
        temp_file.write("def __run_tests():\n")
        temp_file.write("    results = []\n")
        temp_file.write("    try:\n")
        temp_file.write("        obj = Solution()\n")
        temp_file.write("    except Exception as e:\n")
        temp_file.write(
            "        print(json.dumps([{'error': 'Solution class not found'}]))\n")
        temp_file.write("        return\n")

        for tc in test_cases:
            temp_file.write("    try:\n")
            temp_file.write(
                f"        output = obj.{method_name}(**{tc})\n"
            )
            temp_file.write(
                f"        results.append({{'input': {tc}, 'output': output}})\n"
            )
            temp_file.write("    except Exception as e:\n")
            temp_file.write(
                f"        results.append({{'input': {tc}, 'error': str(e)}})\n"
            )

        temp_file.write("    print(json.dumps(results))\n")
        temp_file.write("__run_tests()\n")

    # 2. Execute in a subprocess
    try:
        completed = subprocess.run(
            [sys.executable, file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=TIME_LIMIT_SECONDS
        )

        if completed.stderr:
            return {
                "status": "runtime_error",
                "error": completed.stderr.strip()
            }

        return {
            "status": "ok",
            "results": json.loads(completed.stdout.strip())
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "error": "Time Limit Exceeded"
        }

    finally:
        # 3. Cleanup temp file
        if os.path.exists(file_path):
            os.remove(file_path)
