from django.conf import settings
from django.test.simple import DjangoTestSuiteRunner

class DefaultTestRunner(DjangoTestSuiteRunner):

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        test_labels = settings.TESTS_TO_RUN
        return super(DefaultTestRunner, self).run_tests(test_labels, extra_tests, **kwargs)

