# -*- coding: utf-8 -*-
# pylint: disable=too-many-ancestors

from http import HTTPStatus

from django.contrib.auth.models import Permission
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from tcms.tests import BasePlanCase
from tcms.tests import remove_perm_from_user, user_should_have_perm
from tcms.tests.factories import ClassificationFactory
from tcms.tests.factories import PlanTypeFactory
from tcms.tests.factories import ProductFactory
from tcms.tests.factories import TagFactory
from tcms.tests.factories import TestPlanFactory
from tcms.tests.factories import UserFactory
from tcms.tests.factories import VersionFactory
from tcms.utils.permissions import initiate_user_with_default_setups


class TestViewPlanTags(BasePlanCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        initiate_user_with_default_setups(cls.tester)
        for _i in range(3):
            cls.plan.add_tag(TagFactory())

        cls.unauthorized = UserFactory()
        cls.unauthorized.set_password('password')
        cls.unauthorized.save()

        cls.unauthorized.user_permissions.add(*Permission.objects.all())
        remove_perm_from_user(cls.unauthorized, 'testplans.add_testplantag')
        remove_perm_from_user(cls.unauthorized, 'testplans.delete_testplantag')

    def test_view_tags_with_permissions(self):
        url = reverse('ajax-tags')
        response = self.client.get(url, {'plan': self.plan.pk}, follow=True)
        self.assertEqual(HTTPStatus.OK, response.status_code)

        # assert tag actions are shown
        self.assertContains(response, _('Add Tag'))
        self.assertContains(response,
                            'class="remove js-remove-tag" title="remove tag">%s</a>' %
                            _('Remove'))

    def test_view_tags_without_permissions(self):
        self.client.logout()

        self.client.login(  # nosec:B106:hardcoded_password_funcarg
            username=self.unauthorized.username,
            password='password')

        url = reverse('ajax-tags')
        response = self.client.get(url, {'plan': self.plan.pk}, follow=True)
        self.assertEqual(HTTPStatus.OK, response.status_code)

        # assert tag actions are shown
        self.assertNotContains(response, 'Add Tag')
        self.assertContains(response, '<span class="disabled grey">%s</span>' % _('Remove'))


class TestAddAttachmentView(BasePlanCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.classification = ClassificationFactory(name='Auto')
        cls.product = ProductFactory(name='test', classification=cls.classification)
        cls.product_version = VersionFactory(value='0.1', product=cls.product)
        cls.plan_type = PlanTypeFactory()

        cls.test_plan = TestPlanFactory(name='another test plan for testing',
                                        author=cls.tester,
                                        product=cls.product,
                                        type=cls.plan_type)
        cls.plan_id = cls.test_plan.pk

    def test_add_attachments_view_with_permissions(self):
        user_should_have_perm(self.tester, 'attachments.add_attachment')
        location = reverse('plan-attachment',
                           args=[self.plan_id])
        response = self.client.get(location)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_plan_attachment_missing_priviliges(self):
        remove_perm_from_user(self.tester, 'attachments.add_attachment')
        location = reverse('plan-attachment',
                           args=[self.plan_id])
        response = self.client.get(location)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
