import unittest
import requests
import string
from random import sample

from app import models, create_app, db


def generateRandomString(n=6):
    return "".join(sample(string.ascii_letters, n))


def generateRandomEmail(n=6):
    email = generateRandomString() + "@" + generateRandomString() + ".com"
    return email.lower()


class ApiTestCase(unittest.TestCase):

    def setUp(self):
        self.host = 'http://localhost:5000'
        self.app = create_app(config_name="config.TestingConfig")
        self.client = self.app.test_client
        self.name = generateRandomString()
        self.email = generateRandomEmail()
        self.mock_user = models.User(name=self.name, email=self.email)
        db.session.add(self.mock_user)

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()
            db.session.commit()

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

    def test_users(self):
        response = requests.get(self.host + '/api/v1/users')
        output = response.json()
        self.assertTrue(self.name, output[0]['name'])
        self.assertTrue(self.name, output[0]['email'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
