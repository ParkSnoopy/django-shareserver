from django.test import TestCase, Client

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from lightfileshare.models import SecretFile
from localutils.private_level import PrivateLevel
from localutils.permission_handler import FilePermissionHandler

# Create your tests here.

class FilePermissionTestCase(TestCase):

	def setUp(self):

		file1 = SimpleUploadedFile("dummy-file1.mp4", b"randomFile con-tent.11", content_type="video/mp4")
		SecretFile.objects.create(
			title="dummyfile1--title.mp4",
			content=file1,
			private_level=PrivateLevel.Public,
		)

		file2 = SimpleUploadedFile("dummy-file2.mp4", b"randomFile con-tent.22", content_type="video/mp4")
		SecretFile.objects.create(
			title="dummyfile2--title.mp4",
			content=file2,
			private_level=PrivateLevel.User,
		)

		self.FPH = FilePermissionHandler()
		settings.MY_FILE_PERMISSION_HANDLER = self.FPH

	def test_file_upload_and_permission(self):

		client = Client()

		# s = client.session
		# s.update({
		#     "session_key": 'my_session_key',
		# })
		# s.save()

		# GET
		response = client.get('/', {'json': 'json', 'json data': 'json data'})
		assert response.status_code == 200, "status != 200"

		# POST DATA1
		response = client.post("/details/", data={'id': 1})
		print(f"{response=}")
		assert response.status_code == 302, "status != 302"
		response = client.get(response.url)
		print(f"{response=}")

		self.FPH.check_permission( client, SecretFile.objects.get(pk=2).filename, _debug=True)

		# POST DATA2
		response = client.post("/details/", data={'id': 2})
		print(f"{response=}")
		assert response.status_code == 302, "status != 302"
		assert r"fail=You%20have%20no%20permission%20to%20access%20this%20file" in response.url, f"Err : {response.url}"
		
		self.FPH.set_permission( client, SecretFile.objects.get(pk=2).filename )

		self.FPH.check_permission( client, SecretFile.objects.get(pk=2).filename, _debug=True)

		response = client.post("/details/", data={'id': 2})
		print(f"{response=}")
		assert response.status_code == 302, "status != 302"
		assert r"fail=0" in response.url, f"Err : {response.url}"