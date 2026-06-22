import subprocess
import os
from prefect import flow, task, get_run_logger

@task(name="Run Pytest E2E Suite")
def run_pytest(test_path: str = "tests/"):
    logger = get_run_logger()
    logger.info(f"Running E2E tests in: {test_path}")
    
    # Run pytest and capture output
    result = subprocess.run(
        ["pytest", test_path, "-v", "--tb=short"],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(__file__))
    )
    
    logger.info("Pytest output:\n" + result.stdout)
    if result.stderr:
        logger.error("Pytest errors:\n" + result.stderr)
        
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr
    }

@flow(name="Akdemia Roles E2E Suite")
def run_roles_e2e_tests():
    logger = get_run_logger()
    logger.info("Starting the Akdemia E2E Testing Suite for Roles and Permissions")
    
    result = run_pytest()
    
    if result["returncode"] == 0:
        logger.info("✅ All E2E tests passed successfully!")
    else:
        logger.error("❌ Some tests failed or an error occurred during execution.")
        
    return result

if __name__ == "__main__":
    run_roles_e2e_tests()
