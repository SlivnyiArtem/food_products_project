from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory

from products.admin import User
from products.models import Product, Category, SubCategory
from products.models.user_mtm import UserCartProduct

factory = APIRequestFactory()

class CartTests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.test_user = User.objects.create_user(username='testuser',
                                                  email='',
                                                  password='testpass123')
        self.client.force_login(self.test_user)
        self.test_image = SimpleUploadedFile('test.jpg',
                                             b'',)
        self.test_category = Category.objects.create(
            name='Test Category',
            slug='test-category',
            image=self.test_image,
        )
        self.test_subcategory = SubCategory.objects.create(
            name='TestSubcategory',
            slug='test-subcategory',
            image = self.test_image,
            category = self.test_category
        )
        self.test_product = Product.objects.create(
            name="TestProduct",
            slug="test-product",
            price=5.00,
            subcategory=self.test_subcategory,
        )

    def test_add_to_cart(self):
        url = reverse('cart-add-shopping-cart')
        data = {
            'product_id': self.test_product.id,
            'quantity': 4
        }
        prev_objects_count = UserCartProduct.objects.filter(
            customer=self.test_user).count()
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserCartProduct.objects.filter(
            customer=self.test_user).count(), prev_objects_count+1)
        self.assertEqual(response.data['quantity'], 4)

    def test_add_product_increments_quantity(self):
        url = reverse('cart-add-shopping-cart')
        data = {'product_id': self.test_product.id, 'quantity': 1}
        response_initial = self.client.post(url, data, format='json')
        prev_objects_count = UserCartProduct.objects.filter(
            customer=self.test_user).count()
        self.assertEqual(response_initial.data['quantity'], 1)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(UserCartProduct.objects.filter(
            customer=self.test_user).count(), prev_objects_count)
        self.assertEqual(response.data['quantity'], 2)

    def test_change_quantity(self):
        url = reverse('cart-add-shopping-cart')
        data = {'product_id': self.test_product.id, 'quantity': 1}
        self.client.post(url, data, format='json')
        cart_item = UserCartProduct.objects.get(
            customer=self.test_user,
            product=self.test_product,
        )

        url = reverse('cart-change-quantity')
        data = {'product_id': self.test_product.id, 'quantity': 10}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 10)
        self.assertEqual(response.data['quantity'], cart_item.quantity)


    def test_remove_from_cart(self):
        pass

    def test_checkout_cart(self):
        pass


class CategoryTests(APITestCase):
    def test_checkout_category(self):
        url = reverse('category-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        raise Exception(response.data)
        self.assertEqual(len(response.data['results']), 1)

        first_result = response.data['results'][0]

        self.assertEqual(first_result['name'], 'Овощи')
        self.assertEqual(first_result['slug'], 'vegetables')
        self.assertIn('subcategories', first_result)
        self.assertEqual(len(first_result['subcategories']), 1)

class ProductTests(APITestCase):
    def test_check_product_list(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


