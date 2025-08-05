from functools import wraps


class TestSuite:

    def __init__(self, suite_name: str):
        self.suite_name = suite_name
        self.tests = []

    def test(self, description):

        def decorator(func):

            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    await func(*args, **kwargs)
                    print(f"\033[32m{description} ✓\033[0m")
                    return True
                except Exception as e:
                    print(f"\033[31m{description} ✗\033[0m")
                    print(f"Error: {e}")
                    return False

            self.tests.append(wrapper)
            return wrapper

        return decorator

    async def run(self):
        print(f"Running test suite: '{self.suite_name}' ({len(self.tests)} tests)")
        passed = 0
        failed = 0
        for test in self.tests:
            if await test():
                passed += 1
            else:
                failed += 1
        print(f"Test suite {self.suite_name} completed")
        print(f"Passed: {passed} test(s)")
        print(f"Failed: {failed} test(s)")
