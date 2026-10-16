from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory

from products.admin import User
from products.models import Product, Category
from products.models.user_mtm import UserCartProduct

factory = APIRequestFactory()

class CartTests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.test_user = User.objects.create_user(username='testuser', email='', password='')
        self.client.force_login(self.test_user)
        self.test_image = SimpleUploadedFile('test.jpg',
                                             b'',)
        self.test_subcategory = Category.objects.create(
            name='TestSubcategory',
            slug='testsubcategory',
            image = self.test_image
        )
        self.test_product = Product.objects.create(
            name="TestProduct",
            slug="test-product",
            price=5.00,
            subcategory=self.test_subcategory,
        )

    def test_add_to_cart(self):
        url = '/api/carts/add_shopping_cart/'
        # Todo поменяй на reverse, если это возможно
        data = {
            'product_id': self.test_product.id,
            'quantity': 4
        }

        prev_objects_count = UserCartProduct.objects.filter(
            customer=self.user).count()

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserCartProduct.objects.filter(
            customer=self.user).count(), prev_objects_count+1)
        self.assertEqual(response.data['quantity'], 2)

    def test_remove_from_cart(self):
        pass

    def test_checkout_cart(self):
        pass

    def test_change_quantity(self):
        pass

class CategoryTests(APITestCase):
    def test_add_to_category(self):
        pass

    def test_remove_from_category(self):
        pass

    def test_checkout_category(self):
        pass
