# -*- coding: utf-8 -*-
# pylint: disable=invalid-name

import json

from django.conf import settings
from django.urls import reverse

from tcms.testcases.models import TestCasePlan
from tcms.tests import PermissionsTestCase, factories


class ReorderCasesViewTestCase(PermissionsTestCase):
    """Test case for sorting cases"""
    permission_label = 'testplans.change_testrun'
    http_method_names = ['post']

    @classmethod
    def setUpTestData(cls):

        cls.post_data = {'case': [cls.case_3.pk, cls.case_1.pk]}
        super().setUpTestData()

        cls.cases_url = reverse('plan-reorder-cases', args=[cls.plan.pk])

    def test_order_cases(self):
        self.client.login(  # nosec:B106:hardcoded_password_funcarg
            username=self.plan_tester.username,
            password='password')

        post_data = {'case': [self.case_3.pk, self.case_1.pk]}
        response = self.client.post(self.cases_url, post_data)
        data = json.loads(str(response.content, encoding=settings.DEFAULT_CHARSET))

        self.assertEqual({'rc': 0, 'response': 'ok'}, data)

        case_plan_rel = TestCasePlan.objects.get(plan=self.plan, case=self.case_3)
        self.assertEqual(10, case_plan_rel.sortkey)

        case_plan_rel = TestCasePlan.objects.get(plan=self.plan, case=self.case_1)
        self.assertEqual(20, case_plan_rel.sortkey)
