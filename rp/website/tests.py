from io import BytesIO

from PIL import Image as Img
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.reverse import reverse
from django.test import RequestFactory

from .serializer import *

from rest_framework import status
from rest_framework.test import APITestCase


def create_tier():
    tier, created = Tier.objects.get_or_create(name='beggar', defaults={'thumbnail_s_height': 100}, orginal_link=True,
                                               allow_links=True,  )
    return tier


def create_user():
    user = User.objects.create(username='test4', email='testing@test.com', tier=create_tier(),is_superuser=True)
    user.set_password('test')
    user.save()
    return user


def create_photo():
    image = Img.new('RGB', (100, 100), color='blue')
    image_io = BytesIO()
    image.save(image_io, format='JPEG')
    image_file = SimpleUploadedFile('test_image.jpg', image_io.getvalue(), content_type='image/jpeg')
    return image_file


# MODELS TESTS

class UserTestCase(TestCase):
    def setUp(self):
        self.user = create_user()

    def test_model_creation(self):
        self.assertTrue(self.user)
        self.assertEqual(self.user.username, 'test4')


class TierTestCase(TestCase):
    def setUp(self):
        self.tier = create_tier()

    def test_model_creation(self):
        # tier = Tier.objects.get(name='beggar')
        self.assertTrue(self.tier)
        self.assertEqual(self.tier.name, 'beggar')


class ImageTestCase(TestCase):
    def setUp(self):
        self.user = create_user()
        self.image = Image.objects.create(user=self.user, photo=create_photo())

    def test_model_creation(self):
        self.assertEqual(self.image.user, self.user)
        self.assertTrue(self.image.photo)


class ExpLinkTestCase(TestCase):
    def setUp(self):
        self.user = create_user()
        self.image = Image.objects.create(user=self.user, photo=create_photo())
        self.explink = ExpLink.objects.create(image=self.image, duration=timedelta(seconds=500))

    def test_model_creation(self):
        self.assertEqual(self.explink.image, self.image)
        self.assertTrue(self.explink.expires_at)


# SERIALIZERS TESTS

class UserSerializerTestCase(TestCase):
    def setUp(self):
        self.tier = create_tier()

    def test_valid_serializer(self):
        tier_url = reverse('tier-detail', args=[self.tier.pk])
        data = {
            "id": 1,
            "username": "test",
            "email": "test@test.pl",
            "tier": tier_url,
        }
        serializer = UserSerializer(data=data)

        self.assertTrue(serializer.is_valid())

    def test_invalid_email(self):
        tier_url = reverse('tier-detail', args=[self.tier.pk])
        data = {
            "id": 1,
            "username": "test",
            "email": 21525,
            "tier": tier_url,
        }
        serializer = UserSerializer(data=data)

        self.assertFalse(serializer.is_valid())

    def test_missing_username(self):
        tier_url = reverse('tier-detail', args=[self.tier.pk])
        data = {
            "id": 1,
            "email": 21525,
            "tier": tier_url,
        }
        serializer = UserSerializer(data=data)

        self.assertFalse(serializer.is_valid())


class TierSerializerTestCase(TestCase):
    def test_valid_serializer(self):
        data = {
            "name": 'test',
            "thumbnail_s_height": 200,
            "thumbnail_m_height": 400,
            "orginal_link": True,
            "allow_links": False,
        }
        serializer = TierSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_thumbnail_height(self):
        data = {
            "name": 'test',
            "thumbnail_s_height": -1,
            "thumbnail_m_height": 400,
            "orginal_link": True,
            "allow_links": False,
        }
        serializer = TierSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('thumbnail_s_height', serializer.errors)

    def test_missing_name(self):
        data = {
            "thumbnail_s_height": 200,
            "thumbnail_m_height": 400,
            "orginal_link": True,
            "allow_links": False,
        }
        serializer = TierSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class ImageSerializerTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.tier = create_tier()
        self.user = create_user()
        self.image = Image.objects.create(photo=create_photo(), user=self.user)

    def test_serializer(self):
        request = self.factory.get('/')
        request.user = self.user
        serializer = ImageSerializer(instance=self.image, context={'request': request})
        self.assertIn('thumbnail_s', serializer.data)
        if self.user.tier.thumbnail_m_height != 0:
            self.assertIn('thumbnail_m', serializer.data)
        else:
            self.assertNotIn('thumbnail_m', serializer.data)


class ExpLinkSerializerTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.tier = create_tier()
        self.user = create_user()
        self.image = Image.objects.create(photo=create_photo(), user=self.user)
        self.explink = ExpLink.objects.create(image=self.image, duration=timedelta(seconds=500))

    def test_serializer(self):
        request = self.factory.get('/some-url/')
        request.user = self.user
        serializer = ExpLinkSerializer(instance=self.explink, context={'request': request})
        self.assertIn('photo_url', serializer.data)
        self.assertIn('expires_at', serializer.data)

        image_url = reverse('image-detail', args=[self.image.pk])

        data = {
            'image': image_url,
            'duration': '500'
        }

        serializer = ExpLinkSerializer(data=data, context={'request': request})
        if not serializer.is_valid():
            print(serializer.errors)
        self.assertTrue(serializer.is_valid())

        instance = serializer.save()
        self.assertEqual(instance.image, self.image)
        self.assertEqual(instance.duration, timedelta(seconds=500))



# TESTING VIEWS

class TierViewSetTestCase(APITestCase):

    def setUp(self):
        self.user=create_user()
        self.client.login(username=self.user.username, password='test')
        self.tier_data = {'name': 'test', 'thumbnail_s_height': 200, 'thumbnail_m_height': 400, 'orginal_link': True,
                          'allow_links': False}
        self.response = self.client.post(reverse('tier-list'), self.tier_data, format='json')

    def test_create_tier(self):
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_read_tier_list(self):
        response = self.client.get(reverse('tier-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)



class UserViewSetTestCase(APITestCase):

    def setUp(self):
        self.user = create_user()
        self.client.login(username=self.user.username, password='test')
        self.user_data = {
            "username": "test2",
            "email": "test2@test.com",
            "tier": reverse('tier-detail', args=[self.user.tier.id])
        }
        self.response = self.client.post(reverse('user-list'), self.user_data, format='json')

    def test_create_user(self):
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_read_user_list(self):
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_read_user_detail(self):
        response = self.client.get(reverse('user-detail', args=[self.response.data['id']]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class ImageViewSetTestCase(APITestCase):

    def setUp(self):
        self.tier=create_tier()
        self.user=create_user()
        self.client.login(username=self.user.username, password='test')
        self.image=Image.objects.create(photo=create_photo(), user=self.user)

    def test_list_images(self):
        url = reverse('image-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_image(self):
        url = reverse('image-detail', args=[self.image.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.image.id)

    def test_create_image(self):
        img = create_photo()
        url = reverse('image-list')
        data = {'photo': img}
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Image.objects.count(), 2)




