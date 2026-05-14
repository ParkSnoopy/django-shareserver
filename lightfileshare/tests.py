from urllib.parse import urlencode

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from customauth.models import CustomUser
from lightfileshare import views as lightfileshare_views
from lightfileshare.enums import DetailStatus
from lightfileshare.models import SecretFile
from localutils.hasher import custom_hasher
from localutils.permission_handler import FilePermissionHandler
from localutils.private_level import PrivateLevel


class FileDownloadFlowTestCase(TestCase):
    def setUp(self):
        self.permission_handler = FilePermissionHandler()
        settings.MY_FILE_PERMISSION_HANDLER = self.permission_handler
        lightfileshare_views.FPH = self.permission_handler

        self.public_file = SecretFile.objects.create(
            title="dummy-file-1-pub.mp4",
            content=SimpleUploadedFile(
                "dummy-file-1-pub.mp4", b"1. public content", content_type="video/mp4"
            ),
            private_level=PrivateLevel.Public,
        )
        self.passworded_file = SecretFile.objects.create(
            title="dummy-file-2-passwd.mp4",
            content=SimpleUploadedFile(
                "dummy-file-2-passwd.mp4",
                b"2. secret content",
                content_type="video/mp4",
            ),
            password=custom_hasher("correct-password"),
            private_level=PrivateLevel.Public,
        )
        self.private_file = SecretFile.objects.create(
            title="dummy-file-3-priv.mp4",
            content=SimpleUploadedFile(
                "dummy-file-3-priv.mp4", b"3. private content", content_type="video/mp4"
            ),
            private_level=PrivateLevel.User,
        )
        self.super_private_file = SecretFile.objects.create(
            title="dummy-file-4-super_priv.mp4",
            content=SimpleUploadedFile(
                "dummy-file-4-super_priv.mp4",
                b"4. super private content",
                content_type="video/mp4",
            ),
            private_level=PrivateLevel.Superuser,
        )

    def download_url(self, secret_file):
        return reverse("download", kwargs={"pk": secret_file.pk})

    def fail_url(self, message):
        return f"/?{urlencode({'fail': message})}"

    def assert_has_download_actions(self, response):
        self.assertContains(response, "?disposition=open")
        self.assertContains(response, "?disposition=download")
        self.assertNotContains(response, 'name="password"')

    def assert_has_password_form(self, response):
        self.assertContains(response, 'name="password"')
        self.assertContains(response, "Unlock")
        self.assertNotContains(response, "?disposition=open")
        self.assertNotContains(response, "?disposition=download")

    def test_homepage_links_files_directly_to_download_page(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.download_url(self.public_file))
        self.assertContains(response, self.download_url(self.passworded_file))
        self.assertNotContains(response, 'action="/details/"')
        self.assertNotContains(response, "passwordModal")

    def test_download_page_shows_actions_for_passwordless_file(self):
        response = self.client.get(self.download_url(self.public_file))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "lightfileshare/download.html")
        self.assertContains(response, self.public_file.title)
        self.assert_has_download_actions(response)

    def test_download_page_asks_for_password_before_showing_actions(self):
        response = self.client.get(self.download_url(self.passworded_file))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "lightfileshare/download.html")
        self.assertContains(response, self.passworded_file.title)
        self.assert_has_password_form(response)

    def test_wrong_password_keeps_user_on_password_form_with_error(self):
        response = self.client.post(
            self.download_url(self.passworded_file), data={"password": "wrong-password"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, DetailStatus.FailPassword)
        self.assert_has_password_form(response)

    def test_correct_password_redirects_back_to_download_page_with_actions(self):
        response = self.client.post(
            self.download_url(self.passworded_file),
            data={"password": "correct-password"},
            follow=True,
        )

        self.assertRedirects(response, self.download_url(self.passworded_file))
        self.assert_has_download_actions(response)

    def test_missing_file_redirects_home_with_failure_message(self):
        response = self.client.get(reverse("download", kwargs={"pk": 99999999}))

        self.assertRedirects(
            response,
            self.fail_url(DetailStatus.FailNoFileDownload),
            fetch_redirect_response=False,
        )

    def test_anonymous_user_uses_public_private_level(self):
        response = self.client.get(self.download_url(self.private_file))

        self.assertRedirects(
            response,
            self.fail_url(DetailStatus.FailNoPermission),
            fetch_redirect_response=False,
        )

    def test_logged_in_custom_user_uses_user_private_level(self):
        # not logged in: `User` permission file should not returned
        response = self.client.get(self.download_url(self.private_file))

        self.assertRedirects(
            response,
            self.fail_url(DetailStatus.FailNoPermission),
            fetch_redirect_response=False,
        )

        # logged-in as user: `User` permission file should returned
        user = CustomUser.objects.create_user(
            username="private-level-user", password="test-password"
        )
        user.is_active = True
        user.save()

        self.assertEqual(user.private_level, PrivateLevel.User)
        self.client.force_login(user)
        response = self.client.get(self.download_url(self.private_file))

        self.assertEqual(response.status_code, 200)
        self.assert_has_download_actions(response)

        # logged-in as user: `Superuser` permission file should returned
        response = self.client.get(self.download_url(self.super_private_file))

        self.assertRedirects(
            response,
            self.fail_url(DetailStatus.FailNoPermission),
            fetch_redirect_response=False,
        )

    def test_legacy_details_endpoint_redirects_passwordless_file_to_download_page(self):
        response = self.client.post("/details/", data={"id": self.public_file.pk})

        self.assertRedirects(
            response,
            self.download_url(self.public_file),
            fetch_redirect_response=False,
        )

    def test_legacy_details_endpoint_rejects_private_file_for_anonymous_user(self):
        response = self.client.post("/details/", data={"id": self.private_file.pk})

        self.assertRedirects(
            response,
            self.fail_url(DetailStatus.FailNoPermission),
            fetch_redirect_response=False,
        )
