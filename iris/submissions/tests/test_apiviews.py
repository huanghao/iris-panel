# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This is the REST framework test class for the iris-submissions project REST API.
"""
import urllib

from django.test import TestCase
from django.contrib.auth.models import User

from rest_framework.status import (
    HTTP_200_OK, HTTP_404_NOT_FOUND,
    HTTP_406_NOT_ACCEPTABLE, HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST)

from iris.core.models import (
    Product, Submission, Domain, SubDomain, GitTree, BuildGroup, ImageBuild,
    SubmissionBuild, PackageBuild, Package)
from iris.packagedb.tests.test_apiviews import sort_data

# pylint: disable=no-member,invalid-name,eval-used,too-many-locals,line-too-long,maybe-no-member, too-many-public-methods
#E:266,25: Instance of 'WSGIRequest' has no 'data' member (no-member)
#C:236, 4: Invalid method name "_test_query_not_active_submissions" (invalid-name)
#W:143,19: Use of eval (eval-used)
#R: 73, 4: Too many local variables (18/15) (too-many-locals)
#R: 71, 0: Too many public methods (71/20) (too-many-public-methods)
#E:349,25: Instance of 'WSGIRequest' has no 'status_code' member (but some types could not be inferred) (maybe-no-member)


class SubmissionsTests(TestCase):
    """
    The REST framework test case class of Submissions APIView
    """

    def setUp(self):
        """
        Create 1 Submission instance.
        Create 1 test user.
        """
        self.base_url = '/api/submissions'

        user = User.objects.create_user(username='nemo', password='password', email='nemo@a.com')
        user2 = User.objects.create_user(username='helo', password='ssd', email='hello@a.com')

        product = Product.objects.create(name='Tizen:Common', description='Product')
        product2 = Product.objects.create(name='Tizen:IVI', description='Product2')
        product3 = Product.objects.create(name='Tizen:TV', description='Product3')
        d = Domain.objects.create(name='domain')
        sd = SubDomain.objects.create(name='subdomain', domain=d)
        gt = GitTree.objects.create(gitpath='gitpath', subdomain=sd)
        gt2 = GitTree.objects.create(gitpath='a/b/c', subdomain=sd)

        submission_name_status = {
            'submit/product/20140321.223750': [('20_IMGBUILDING', product, gt, user), ('20_IMGBUILDING', product, gt2, user)],
            'submit/product/20140421.223750': [('15_PKGFAILED', product, gt, user), ('15_PKGFAILED', product, gt2, user2)],
            'submit/product/20140521.223750': [('15_PKGFAILED', product, gt, user)],
            'submit/product/20140621.223750': [('33_ACCEPTED', product, gt, user)],
            'submit/product/20140721.223750': [('36_REJECTED', product, gt, user)],
            'submit/product/20140821.223750': [('15_PKGFAILED', product2, gt, user)],
            'submit/product/20140921.223750': [('10_PKGBUILDING', product3, gt, user)],
            'submit/product/20140121.223750': [('SUBMITTED', None, gt, user)],
        }
        for key, value in submission_name_status.iteritems():
            for status, product, gittree, user in value:
                sb1 = Submission.objects.create(
                    name=key,
                    commit='2ae265f9820cb36e',
                    owner=user,
                    gittree=gittree,
                    status=status)
                if status != 'SUBMITTED':
                    bg1, _ = BuildGroup.objects.get_or_create(
                        name='home:pre-release:%s:%s' %(product.name, key),
                        status=status)
                    SubmissionBuild.objects.create(
                        submission=sb1,
                        product=product,
                        group=bg1)

        bg = BuildGroup.objects.get(name='home:pre-release:Tizen:Common:submit/product/20140421.223750')
        image_data = [
            ('mobile-boot-armv7l-RD-PQ', 'SUCCESS', 'http://download.xx.org/prerelease/tizen/20150128.3/images/arm-x11/mobile-boot-armv7l-RD-PQ'),
            ('mobile-x11-3parts-arm64', 'BUILDING', 'http://download.xx.org/prerelease/tizen/20150128.3/images/arm-x11/mobile-x11-3parts-arm64'),
            ('mobile-x11-3parts-armv7l', 'FAILURE', 'http://download.xx.org/prerelease/tizen/20150128.3/images/arm-x11/mobile-x11-3parts-armv7l'),
        ]
        for name, status, url in image_data:
            ImageBuild.objects.create(name=name, status=status, url=url, group=bg)

    def test_get_query_all(self):
        """
        GET full list of submissions
        """
        url = '%s/' % self.base_url
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        data = [{
            'submission': 'submit/product/20140321.223750',
            'status': 'Image building',
            'product': 'Tizen:Common',
            'gittrees': ['a/b/c', 'gitpath']
        }, {
            'submission': 'submit/product/20140421.223750',
            'status': 'Package building failed',
            'product': 'Tizen:Common',
            'gittrees': ['a/b/c', 'gitpath']
        }, {
            'submission': 'submit/product/20140521.223750',
            'status': 'Package building failed',
            'product': 'Tizen:Common',
            'gittrees': ['gitpath']
        },
        {
            'submission': 'submit/product/20140821.223750',
            'status': 'Package building failed',
            'product': 'Tizen:IVI',
            'gittrees': ['gitpath']
        },
        {
            'submission': 'submit/product/20140921.223750',
            'status': 'Package building',
            'product': 'Tizen:TV',
            'gittrees': ['gitpath']
        }
        ]
        res_data = eval(response.content)
        sort_data(data)
        sort_data(res_data)
        self.assertEqual(res_data, data)

    def test_get_query_by_product(self):
        """
        GET full list of submissions of product: Tizen:Common
        """
        url = '%s/Tizen:Common/' % self.base_url
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        data = [{
            'submission': 'submit/product/20140321.223750',
            'status': 'Image building',
            'gittrees': ['a/b/c', 'gitpath']
        }, {
            'submission': 'submit/product/20140421.223750',
            'status': 'Package building failed',
            'gittrees': ['a/b/c', 'gitpath']
        }, {
            'submission': 'submit/product/20140521.223750',
            'status': 'Package building failed',
            'gittrees': ['gitpath']
        }]
        res_data = eval(response.content)
        sort_data(data)
        sort_data(res_data)
        self.assertEqual(res_data, data)

    def test_query_specific_submission(self):
        """
         GET submissions by name.
        """
        url = '%s/Tizen:Common/submit/product/20140421.223750/' % self.base_url
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        res_data = eval(response.content)
        data = {
            'submission': 'submit/product/20140421.223750',
            'target_project': 'Tizen:Common',
            'commit': ['2ae265f9820cb36e'],
            'submitter': ['nemo@a.com', 'hello@a.com'],
            'download_url': 'http://download.xx.org/prerelease/tizen/20150128.3/',
            'git_trees': ['a/b/c', 'gitpath'],
            'images': [
                        ['mobile-boot-armv7l-RD-PQ', 'Succeeded'],
                        ['mobile-x11-3parts-arm64', 'Building'],
                        ['mobile-x11-3parts-armv7l', 'Failed'],
                       ],
        }
        sort_data(data)
        sort_data(res_data)

        self.assertEqual(res_data, data)

    def test_query_specific_submission_without_product(self):
        """
         GET submissions by name.
        """
        url = '%s/Tizen:Common/submit/product/20140121.223750/' % self.base_url
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_query_specific_submission_without_images(self):
        """
         GET submissions by name.
        """
        url = '%s/Tizen:Common/submit/product/20140521.223750/' % self.base_url
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        res_data = eval(response.content)
        data = {
            'submission': 'submit/product/20140521.223750',
            'target_project': 'Tizen:Common',
            'commit': ['2ae265f9820cb36e'],
            'submitter': ['nemo@a.com'],
            'download_url': '',
            'git_trees': ['gitpath'],
            'images': [],
        }
        sort_data(data)
        sort_data(res_data)
        self.assertEqual(res_data, data)

    def test_query_specific_submission_without_packages(self):
        """
         GET submissions by name.
        """
        url = '%s/Tizen:TV/submit/product/20140921.223750/' % self.base_url
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        res_data = eval(response.content)
        data = {
            'submission': 'submit/product/20140921.223750',
            'target_project': 'Tizen:TV',
            'commit': ['2ae265f9820cb36e'],
            'submitter': ['nemo@a.com'],
            'download_url': '',
            'git_trees': ['gitpath'],
            'images': [],
        }
        sort_data(data)
        sort_data(res_data)
        self.assertEqual(res_data, data)

    def test_query_not_exist_specific_submission(self):
        """
         GET submissions by name.
        """
        url = '%s/Tizen:Common/submit/product/201021.223750/' % self.base_url
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_query_by_un_exist_product(self):
        """
        Test failed query by querying non-existing product
        """
        url = '%s/this_product_doesnt_exist/' % self.base_url
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(eval(response.content), [])

    def test_query_by_status_with_product(self):
        """
        GET submissions by status
        """
        url = '%s/Tizen:Common/?status=%s' % \
              (self.base_url, urllib.quote('Package building failed'))
        data = [{
            'submission': 'submit/product/20140421.223750',
            'status': 'Package building failed',
            'gittrees': ['a/b/c', 'gitpath']
        }, {
            'submission': 'submit/product/20140521.223750',
            'status': 'Package building failed',
            'gittrees': ['gitpath']
        }]
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        res_data = eval(response.content)
        sort_data(data)
        sort_data(res_data)
        self.assertEqual(res_data, data)

    def test_query_by_multi_status_with_product(self):
        """
        GET submissions by status
        """
        url = '%s/Tizen:Common/?status=%s,%s,%s' % \
              (self.base_url, urllib.quote('Package building failed'),
                urllib.quote('Image building'),
                urllib.quote('accepted'))
        data = [{
            'submission': 'submit/product/20140421.223750',
            'status': 'Package building failed',
            'gittrees': ['a/b/c', 'gitpath']
        }, {
            'submission': 'submit/product/20140521.223750',
            'status': 'Package building failed',
            'gittrees': ['gitpath']
        },{
            'submission': 'submit/product/20140321.223750',
            'status': 'Image building',
            'gittrees': ['a/b/c', 'gitpath']
        },{
            'submission': 'submit/product/20140621.223750',
            'status': 'Accepted',
            'gittrees': ['gitpath']
        }]
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        res_data = eval(response.content)
        sort_data(data)
        sort_data(res_data)
        self.assertEqual(res_data, data)

    def test_query_by_multi_status_without_product(self):
        """
        GET submissions by status
        """
        url = '%s/?status=%s,%s' % \
              (self.base_url,
               urllib.quote('rejected'),
               urllib.quote('accepted'))
        data = [{
            'submission': 'submit/product/20140721.223750',
            'status': 'Rejected',
            'product': 'Tizen:Common',
            'gittrees': ['gitpath']
        },{
            'submission': 'submit/product/20140621.223750',
            'status': 'Accepted',
            'product': 'Tizen:Common',
            'gittrees': ['gitpath']
        }]
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        res_data = eval(response.content)
        sort_data(data)
        sort_data(res_data)
        self.assertEqual(res_data, data)

    def test_by_un_exist_status(self):
        """
        Test failed query by querying non-existing status
        """
        url = '%s/Tizen:Common/?status=hello' % self.base_url
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(eval(response.content), [])

    def test_case_insensitive_status(self):
        """
        Test that status can be case insensitive
        """
        url = '%s/Tizen:Common/?status=%s' % \
            (self.base_url, urllib.quote('image building'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        data = [{
            'submission': 'submit/product/20140321.223750',
            'status': 'Image building',
            'gittrees': ['gitpath', 'a/b/c']
            }]
        res_data = eval(response.content)
        sort_data(data)
        sort_data(res_data)
        self.assertEqual(res_data, data)
