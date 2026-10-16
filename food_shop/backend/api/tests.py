from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from products.admin import User
from products.models import Category, Product, SubCategory
from products.models.product import ProductImage
from products.models.user_mtm import UserCartProduct

factory = APIRequestFactory()


class BaseFoodShopAPITestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        self.test_image = SimpleUploadedFile(
            "test.jpg",
            b"",
        )
        self.test_category = Category.objects.create(
            name="Test Category",
            slug="test-category",
            image=self.test_image,
        )
        self.test_subcategory = SubCategory.objects.create(
            name="TestSubcategory",
            slug="test-subcategory",
            image=self.test_image,
            category=self.test_category,
        )
        self.test_product = Product.objects.create(
            name="TestProduct",
            slug="test-product",
            price=5.00,
            subcategory=self.test_subcategory,
        )

        self.test_product_image = ProductImage.objects.create(
            product=self.test_product,
            image=self.test_image,
            size_order=0,
        )

    def add_to_cart(self, quantity=2):
        url = reverse("cart-add-shopping-cart")
        data = {"product_id": self.test_product.id,
                "quantity": quantity}
        return self.client.post(url, data, format="json")


class CartTests(BaseFoodShopAPITestCase):
    def setUp(self):
        super().setUp()
        self.test_user = User.objects.create_user(
            username="testuser", email="",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.test_user)

    def test_add_to_cart(self):
        prev_objects_count = UserCartProduct.objects.filter(
            customer=self.test_user
        ).count()
        response = self.add_to_cart(4)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            UserCartProduct.objects.filter(
                customer=self.test_user).count(),
            prev_objects_count + 1,
        )
        self.assertEqual(response.data["quantity"], 4)

    def test_add_product_increm_quantity(self):
        response_initial = self.add_to_cart()
        prev_objects_count = UserCartProduct.objects.filter(
            customer=self.test_user
        ).count()

        self.assertEqual(response_initial.data["quantity"], 2)

        response = self.add_to_cart()

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(
            UserCartProduct.objects.filter(customer=self.test_user).count(),
            prev_objects_count,
        )
        self.assertEqual(response.data["quantity"], 4)

    def test_change_quantity(self):
        self.add_to_cart()
        cart_item = UserCartProduct.objects.get(
            customer=self.test_user,
            product=self.test_product,
        )

        url = reverse("cart-set-product-quantity")
        data = {"product_id": self.test_product.id, "quantity": 10}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 10)
        self.assertEqual(response.data["quantity"], cart_item.quantity)

    def test_remove_from_cart(self):
        self.add_to_cart()

        url = reverse(
            "cart-delete-product-from-shopping-cart",
            kwargs={"pk": self.test_product.id},
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            UserCartProduct.objects.filter(
                customer=self.test_user, product=self.test_product
            ).exists()
        )

    def test_clear_cart(self):
        self.add_to_cart()

        url = reverse("cart-clear-cart")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            UserCartProduct.objects.filter(
                customer=self.test_user,
            ).count(),
            0,
        )

    def test_checkout_cart(self):
        self.add_to_cart()

        url = reverse("cart-list")
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("items", response.data)
        self.assertEqual(len(response.data["items"]), 1)

        request = RequestFactory().get("/")
        expected_image_data = [
            {
                "image": request.build_absolute_uri(
                    self.test_product_image.image.url
                ),
                "size_order": 0,
            }
        ]

        correct_product_data = {
            "slug": self.test_product.slug,
            "subcategory": self.test_subcategory.name,
            "category": self.test_category.name,
            "name": self.test_product.name,
            "price": "5.00",
        }

        result_cart = response.data["items"][0]
        self.assertEqual(result_cart["product"]["images"],
                         expected_image_data)
        result_cart["product"].pop("images")

        self.assertEqual(result_cart["total_price"],
                         10.00)
        self.assertEqual(result_cart["quantity"], 2)
        self.assertEqual(result_cart["product"],
                         correct_product_data)


class CategoryTests(BaseFoodShopAPITestCase):
    def test_checkout_category(self):
        SubCategory.objects.create(
            name="2nd Test SubCategory",
            slug="2nd-test-subcategory",
            image=self.test_image,
            category=self.test_category,
        )

        url = reverse("category-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)
        self.assertIn("results", response.data)

        self.assertGreaterEqual(len(response.data["results"]), 1)

        category = next(
            (
                cat
                for cat in response.data["results"]
                if cat["slug"] == self.test_category.slug
            ),
            None,
        )
        self.assertIsNotNone(category)
        self.assertEqual(category["name"], self.test_category.name)
        self.assertEqual(category["slug"], self.test_category.slug)

        self.assertIn("subcategories", category)
        self.assertGreaterEqual(len(category["subcategories"]), 2)

        subcategory = next(
            (
                s
                for s in category["subcategories"]
                if s["slug"] == self.test_subcategory.slug
            ),
            None,
        )
        self.assertIsNotNone(subcategory)
        self.assertEqual(subcategory["name"], self.test_subcategory.name)
        request = RequestFactory().get("/")
        correct_subcategory_data = {
            "name": self.test_subcategory.name,
            "slug": self.test_subcategory.slug,
            "image": request.build_absolute_uri(
                self.test_subcategory.image.url
            ),
        }

        self.assertEqual(subcategory, correct_subcategory_data)


class ProductTests(BaseFoodShopAPITestCase):
    def test_check_product_list(self):
        url = reverse("product-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertGreaterEqual(len(response.data["results"]), 1)

        product = next(
            (
                prod
                for prod in response.data["results"]
                if prod["slug"] == self.test_product.slug
            ),
            None,
        )
        self.assertIsNotNone(product)
        self.assertEqual(
            set(product.keys()),
            {"name", "slug", "subcategory", "category", "price", "images"},
        )
