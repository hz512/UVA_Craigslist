from unittest import skip

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase, override_settings
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver

from .models import *
from users.models import CustomUser
from .templatetags.formatters import format_brief_description

USER_NAME = "tj1819"
COMPUTING_ID = "tj5ca"
FIRST_NAME = "Thomas"
LAST_NAME = "Jefferson"
EMAIL = COMPUTING_ID + "@virginia.edu"
PASSWORD = "pAsswrd123!!"
PHONE_NUMBER = "5555555555"
COMPUTING_ID = "tj5ca"
BIO = "I'M TJ!"

TITLE = "Test Post"
PRICE = "10.0"
DESCRIPTION = "this is a description"

class ProfileTest(TestCase):
    def setUp(self):
        """
        Create a user through direct method calls for testing.
        """
        self.test_user = CustomUser.objects.create_user(
            username=USER_NAME, email=EMAIL,
            password=PASSWORD, bio=BIO,
            phone_number=PHONE_NUMBER,
            computing_id=COMPUTING_ID,
        )

    def test_get_profile(self):
        """
        Tests profile access through a user, and whether that profile's associated user model is correct.
        """
        profile = self.test_user.profile
        self.assertEqual(profile.user, self.test_user, "Test if looked up profile's user and created user match.")

    def test_profile_to_string_no_names(self):
        """
        Given a profile with only a first and last name, test that the profile as a string is just the username.
        """
        self.assertEquals(self.test_user.username, str(self.test_user.profile))

    def test_profile_to_string_first_name(self):
        """
        Given a profile with only a first name, test that the profile as a string is just the first name.
        """
        user = CustomUser.objects.create_user(
            username=USER_NAME + "3", first_name=FIRST_NAME,
            email=COMPUTING_ID + "3" + "@virginia.edu", password=PASSWORD
        )
        self.assertEquals(FIRST_NAME, str(user.profile))

    def test_profile_to_string_last_name(self):
        """
        Given a profile with only a last name, test that the profile as a string is just the last name.
        """
        user = CustomUser.objects.create_user(
            username=USER_NAME + "4", last_name=LAST_NAME,
            email=COMPUTING_ID + "4" + "@virginia.edu", password=PASSWORD
        )
        self.assertEquals(LAST_NAME, str(user.profile))

    def test_profile_to_string_both_names(self):
        """
        Given a profile with only a first and last name, test that the profile as a string is both names and a space.
        """
        user = CustomUser.objects.create_user(
            username=USER_NAME + "5", first_name=FIRST_NAME, last_name=LAST_NAME,
            email=COMPUTING_ID + "5" + "@virginia.edu", password=PASSWORD
        )
        self.assertEquals(f"{FIRST_NAME} {LAST_NAME}", str(user.profile))


class PostTest(TestCase):
    def setUp(self):
        """
        Create a user through direct method calls for testing and create a post for the user
        """
        self.test_user = CustomUser.objects.create_user(
            username=USER_NAME, email=EMAIL,
            password=PASSWORD, bio=BIO,
            phone_number=PHONE_NUMBER,
            computing_id=COMPUTING_ID,
        )
        self.test_post = self.test_user.create_post(title="Test post", description="Description.", price=2.00)

    def test_was_published_in_30days_future_post(self):
        future_time = timezone.now() + datetime.timedelta(days=30)
        future_post = Post(pub_date=future_time)
        self.assertFalse(future_post.was_published_in_30days())

    def test_was_published_in_30days_old_post(self):
        old_time = timezone.now() - datetime.timedelta(days=50)
        old_post = Post(pub_date=old_time)
        self.assertFalse(old_post.was_published_in_30days())

    def test_was_published_in_30days_recent_post(self):
        recent_time = timezone.now() - datetime.timedelta(days=10)
        recent_post = Post(pub_date=recent_time)
        self.assertTrue(recent_post.was_published_in_30days())

    def test_was_published_in_30days_edge_post(self):
        edge_time = timezone.now() - datetime.timedelta(days=30)
        edge_post = Post(pub_date=edge_time)
        self.assertFalse(edge_post.was_published_in_30days())

    def test_was_published_in_180days_future_post(self):
        future_time = timezone.now() + datetime.timedelta(days=180)
        future_post = Post(pub_date=future_time)
        self.assertFalse(future_post.was_published_in_180days())

    def test_was_published_in_180days_old_post(self):
        old_time = timezone.now() - datetime.timedelta(days=200)
        old_post = Post(pub_date=old_time)
        self.assertFalse(old_post.was_published_in_180days())

    def test_was_published_in_180days_recent_post(self):
        recent_time = timezone.now() - datetime.timedelta(days=10)
        recent_post = Post(pub_date=recent_time)
        self.assertTrue(recent_post.was_published_in_180days())

    def test_was_published_in_180days_edge_post(self):
        edge_time = timezone.now() - datetime.timedelta(days=180)
        edge_post = Post(pub_date=edge_time)
        self.assertFalse(edge_post.was_published_in_180days())

    def test_create_post(self):
        """
        Create a post.
        """
        self.assertIn(self.test_post, Post.objects.all(), "Check if post is created in database.")

    def test_update_post(self):
        """
        Update a post.
        """
        self.test_post.description = "Updated description"
        self.test_post.save()
        self.assertNotEqual("Description.", self.test_post.description)

    def test_delete_post(self):
        """
        Create a post.
        """
        tmp_post = Post.objects.create(
            title="Temp Post", description="xxx", price=1.00, owner=self.test_user
        )
        tmp_post.save()
        self.assertIn(tmp_post, Post.objects.all())
        tmp_post.delete()
        self.assertNotIn(tmp_post, Post.objects.all())

    def test_post_to_string(self):
        """
        Test the to string method of Post class
        """
        self.assertEqual("Test post created by tj1819", str(self.test_post))


class MessageTest(TestCase):
    def setUp(self):
        """
        Create a sender, a receiver, a post, and some message between the two users
        """
        self.sender = CustomUser.objects.create_user(
            username=USER_NAME, email=EMAIL,
            password=PASSWORD, bio=BIO,
            phone_number=PHONE_NUMBER,
            computing_id=COMPUTING_ID,
        )
        self.receiver = CustomUser.objects.create_user(
            username="haoranzhu", email="hz3fr@virginia.edu",
            computing_id="hz3fr", password="hahaha123@"
        )
        self.test_post = self.sender.create_post(title="Test post", description="Description.", price=2.00)
        self.test_message1 = self.sender.send_message(self.test_post, "This is the message text.")
        self.test_message2 = Message.objects.create(
            sender=self.sender, to_post=self.test_post,
            receiver=self.receiver.username, text="Hello World!",
        )

    def test_send_message(self):
        """
        Send a message to a post.
        """
        self.assertIn(self.test_message1, Message.objects.all(), "Check if the message was created.")

    def test_message_to_string(self):
        self.assertEqual("tj1819 to Test post created by tj1819", str(self.test_message2))

    def test_message_unread(self):
        self.assertFalse(self.test_message2.read)


@override_settings(DEBUG=True)
class SystemTest(StaticLiveServerTestCase):
    def setUp(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--disable_gpu")
        self.selenium = WebDriver(chrome_options=self.chrome_options)
        super(SystemTest, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(SystemTest, self).tearDown()

    def fill_out_sign_up(self):
        """
        Fills out all of the blanks on the sign up form.
        """
        field = self.selenium.find_element_by_name("first_name")
        field.send_keys(FIRST_NAME)
        field = self.selenium.find_element_by_name("last_name")
        field.send_keys(LAST_NAME)
        field = self.selenium.find_element_by_name("computing_id")
        field.send_keys(COMPUTING_ID)
        field = self.selenium.find_element_by_name("email")
        field.send_keys(EMAIL)
        field = self.selenium.find_element_by_name("phone_number")
        field.send_keys(PHONE_NUMBER)
        field = self.selenium.find_element_by_name("bio")
        field.send_keys(BIO)
        field = self.selenium.find_element_by_name("username")
        field.send_keys(USER_NAME)
        field = self.selenium.find_element_by_name("password1")
        field.send_keys(PASSWORD)
        field = self.selenium.find_element_by_name("password2")
        field.send_keys(PASSWORD)
        field.submit()

    def fill_out_log_in(self):
        field = self.selenium.find_element_by_name("username")
        field.send_keys(USER_NAME)
        field = self.selenium.find_element_by_name("password")
        field.send_keys(PASSWORD)
        field.submit()

    def test_sign_up1(self):
        """
        The user must be able to sign up through the form.
        """
        self.selenium.get(f"{self.live_server_url}/users/signup/")
        self.fill_out_sign_up()
        # Check if redirected back to main page and notified.
        self.assertTrue(f"Account created for {USER_NAME}!" in self.selenium.page_source)

    def test_sign_up2(self):
        self.selenium.get(f"{self.live_server_url}/users/signup/")
        self.fill_out_sign_up()
        # Check if user and profile actually created for user.
        user_query_set = CustomUser.objects.filter(username__exact=USER_NAME)
        self.assertTrue(user_query_set.exists())
        self.assertTrue(user_query_set[0].profile is not None)

    def test_log_in(self):
        self.selenium.get(f"{self.live_server_url}/users/signup/")
        self.fill_out_sign_up()
        self.selenium.get(f"{self.live_server_url}/users/login/")
        self.fill_out_log_in()
        self.assertTrue(f"Profile" in self.selenium.page_source)
        self.assertTrue(f"Log out" in self.selenium.page_source)

    def signUpAndLogIn(self):
        self.selenium.get(f"{self.live_server_url}/users/signup/")
        self.fill_out_sign_up()
        self.selenium.get(f"{self.live_server_url}/users/login/")
        self.fill_out_log_in()

    def test_log_out(self):
        self.signUpAndLogIn()
        self.selenium.get(f"{self.live_server_url}/users/logout/")
        self.assertTrue(f"You have been logged out." in self.selenium.page_source)

    def test_sign_up_no_username(self):
        """
        The user must enter all fields in order to make an account.
        """
        self.selenium.get(f"{self.live_server_url}/users/signup/")
        field = self.selenium.find_element_by_name("first_name")
        field.send_keys(FIRST_NAME)
        field = self.selenium.find_element_by_name("last_name")
        field.send_keys(LAST_NAME)
        field = self.selenium.find_element_by_name("computing_id")
        field.send_keys(COMPUTING_ID)
        field = self.selenium.find_element_by_name("email")
        field.send_keys(EMAIL)
        field = self.selenium.find_element_by_name("phone_number")
        field.send_keys(PHONE_NUMBER)
        field = self.selenium.find_element_by_name("password1")
        field.send_keys(PASSWORD)
        field = self.selenium.find_element_by_name("password2")
        field.send_keys(PASSWORD)
        field.submit()

        # Shouldn't be able to create the account.
        self.assertFalse(
            f"Account created for {USER_NAME}!" in self.selenium.page_source)
        # Check if user not created.
        user_query_set = CustomUser.objects.filter(username__exact=USER_NAME)
        self.assertFalse(user_query_set.exists())

    def test_no_profile_before_login(self):
        self.selenium.get(f"{self.live_server_url}/main/")
        self.assertFalse(f"Profile" in self.selenium.page_source)

    def test_no_logout_before_login(self):
        self.selenium.get(f"{self.live_server_url}/main/")
        self.assertFalse(f"Log out" in self.selenium.page_source)

    def test_login_before_login(self):
        self.selenium.get(f"{self.live_server_url}/main/")
        self.assertTrue(f"Log in" in self.selenium.page_source)

    def test_signup_before_login(self):
        self.selenium.get(f"{self.live_server_url}/main/")
        self.assertTrue(f"Sign up" in self.selenium.page_source)

    def test_no_login_after_login(self):
        self.signUpAndLogIn()
        self.selenium.get(f"{self.live_server_url}/main/")
        self.assertFalse(f"Log in" in self.selenium.page_source)

    def test_no_signup_after_login(self):
        self.signUpAndLogIn()
        self.selenium.get(f"{self.live_server_url}/main/")
        self.assertFalse(f"Sign up" in self.selenium.page_source)


    def fill_out_make_post(self):
        field = self.selenium.find_element_by_name("title")
        field.send_keys(TITLE)
        field = self.selenium.find_element_by_name("price")
        field.send_keys(PRICE)
        field = self.selenium.find_element_by_name("description")
        field.send_keys(DESCRIPTION)
        field.submit()

    def test_make_post(self):
        """
        Test that a user can make a post to sell something through the web page.
        """
        self.signUpAndLogIn()
        self.selenium.get(f"{self.live_server_url}/main/makepost/")
        self.fill_out_make_post()
        self.assertTrue(f"You have created a new post! You can now view it in your profile." in self.selenium.page_source)
        post_query_set = Post.objects.filter(title__exact=TITLE)
        self.assertTrue(post_query_set.exists())
        self.assertGreaterEqual(post_query_set.count(), 1)

    def make_a_post(self):
        self.signUpAndLogIn()
        self.selenium.get(f"{self.live_server_url}/main/makepost/")
        self.fill_out_make_post()
        post_query_set = Post.objects.filter(title__exact=TITLE, description__exact=DESCRIPTION)
        self.post = post_query_set[0]
        self.post_id = str(self.post.post_id)

    def fill_out_update_post(self):
        field = self.selenium.find_element_by_name("title")
        field.send_keys("Updated Title")
        field.submit()

    def test_update_post(self):
        """
        Test that a user can update their post
        """
        self.make_a_post()
        self.selenium.get(f"{self.live_server_url}/main/{USER_NAME}/post_{self.post_id}/update/")
        self.fill_out_update_post()
        self.assertTrue(f"Your post has been updated!" in self.selenium.page_source)
        self.assertTrue(f"Updated Title" in self.selenium.page_source)
    
    def test_delete_post(self):
        """
        Test that a user can delete post
        """
        self.make_a_post()
        self.selenium.get(f"{self.live_server_url}/main/{USER_NAME}/post_{self.post_id}/delete/done/")
        self.assertTrue(f"Your post has been deleted!" in self.selenium.page_source)

    def test_update_profile(self):
        """
        Test that a user can update their profile
        """
        self.signUpAndLogIn()
        self.selenium.get(f"{self.live_server_url}/main/profile/edit/")
        field = self.selenium.find_element_by_name("username")
        field.send_keys("Updated Username")
        field.submit()
        self.assertTrue(f"Your account has been updated!" in self.selenium.page_source)

    def test_nonlogin_profile(self):
        self.signUpAndLogIn()
        self.selenium.get(f"{self.live_server_url}/main/{USER_NAME}/")
        self.assertFalse(f"Edit Profile" in self.selenium.page_source)


    def test_leave_message_loadpage_failure(self):
        self.make_a_post()
        self.selenium.get(f"{self.live_server_url}/main/{USER_NAME}/post_{self.post_id}/dialogue_with_{USER_NAME}/")
        self.assertTrue(f"Owner cannot have a conversation with himself/herself/theirselves!" in self.selenium.page_source)

    def another_user_log_in(self):
        self.selenium.get(f"{self.live_server_url}/users/signup/")
        field = self.selenium.find_element_by_name("first_name")
        field.send_keys("Haoran")
        field = self.selenium.find_element_by_name("last_name")
        field.send_keys("Zhu")
        field = self.selenium.find_element_by_name("computing_id")
        field.send_keys("hz3fr")
        field = self.selenium.find_element_by_name("email")
        field.send_keys("hz3fr@virginia.edu")
        field = self.selenium.find_element_by_name("phone_number")
        field.send_keys("4344662282")
        field = self.selenium.find_element_by_name("bio")
        field.send_keys("Hi")
        field = self.selenium.find_element_by_name("username")
        field.send_keys("haoranzhu")
        field = self.selenium.find_element_by_name("password1")
        field.send_keys("hahaha123@")
        field = self.selenium.find_element_by_name("password2")
        field.send_keys("hahaha123@")
        field.submit()
        self.selenium.get(f"{self.live_server_url}/users/login/")
        field = self.selenium.find_element_by_name("username")
        field.send_keys("haoranzhu")
        field = self.selenium.find_element_by_name("password")
        field.send_keys("hahaha123@")
        field.submit()

    def test_leave_message_loadpage_success(self):
        self.make_a_post()
        self.selenium.get(f"{self.live_server_url}/users/logout/")
        self.another_user_log_in()
        self.selenium.get(f"{self.live_server_url}/main/{USER_NAME}/post_{self.post_id}/dialogue_with_haoranzhu/")
        self.assertTrue(f"You haven't sent a message yet." in self.selenium.page_source)

    def test_leave_message(self):
        self.make_a_post()
        self.selenium.get(f"{self.live_server_url}/users/logout/")
        self.another_user_log_in()
        self.selenium.get(f"{self.live_server_url}/main/{USER_NAME}/post_{self.post_id}/dialogue_with_haoranzhu/")
        field = self.selenium.find_element_by_name("text")
        field.send_keys("hi")
        field.submit()
        self.assertTrue(f"hi" in self.selenium.page_source)

    def leave_a_message(self):
        self.make_a_post()
        self.selenium.get(f"{self.live_server_url}/users/logout/")
        self.another_user_log_in()
        self.selenium.get(f"{self.live_server_url}/main/{USER_NAME}/post_{self.post_id}/dialogue_with_haoranzhu/")
        field = self.selenium.find_element_by_name("text")
        field.send_keys("hi")
        field.submit()
        self.selenium.get(f"{self.live_server_url}/users/logout/")
        self.selenium.get(f"{self.live_server_url}/users/login/")
        self.fill_out_log_in()

    def test_all_messages(self):
        self.leave_a_message()
        self.selenium.get(f"{self.live_server_url}/main/{USER_NAME}/post_{self.post_id}/all_messages/")
        self.assertTrue(f"Dialogue with haoranzhu" in self.selenium.page_source)

    def test_unread_message(self):
        self.leave_a_message()
        self.selenium.get(f"{self.live_server_url}/main/profile/")
        self.assertTrue(f"Your have 1 unread messages." in self.selenium.page_source)

    def test_read_message(self):
        self.leave_a_message()
        self.selenium.get(f"{self.live_server_url}/main/{USER_NAME}/post_{self.post_id}/dialogue_with_haoranzhu/")
        self.selenium.get(f"{self.live_server_url}/main/profile/")
        self.assertFalse(f"Your have 1 unread messages." in self.selenium.page_source)


    def test_search_results(self):
        self.make_a_post()
        self.selenium.get(f"{self.live_server_url}/main/")
        field = self.selenium.find_element_by_name("data")
        field.send_keys("test")
        field.submit()
        self.assertTrue(f"Test Post" in self.selenium.page_source)

    def test_categories(self):
        self.make_a_post()
        self.selenium.get(f"{self.live_server_url}/main/allposts/study_supplies/")
        self.assertTrue(f"Test Post" in self.selenium.page_source)

    def test_update_others_post(self):
        self.make_a_post()
        self.selenium.get(f"{self.live_server_url}/users/logout/")
        self.another_user_log_in()
        self.selenium.get(f"{self.live_server_url}/main/{USER_NAME}/post_{self.post_id}/update/")
        self.assertTrue(f"Username didn't match. Please log in the author's account to update this post" in self.selenium.page_source)

    def test_delete_others_post(self):
        self.make_a_post()
        self.selenium.get(f"{self.live_server_url}/users/logout/")
        self.another_user_log_in()
        self.selenium.get(f"{self.live_server_url}/main/{USER_NAME}/post_{self.post_id}/delete/")
        self.assertTrue(f"Username didn't match. Please log in the author's account to delete this post" in self.selenium.page_source)

    def test_all_posts(self):
        self.make_a_post()
        self.selenium.get(f"{self.live_server_url}/main/allposts/")
        self.assertTrue(f"Test Post" in self.selenium.page_source)

    def test_all_posts_30days(self):
        self.make_a_post()
        self.selenium.get(f"{self.live_server_url}/main/allposts/30days/")
        self.assertTrue(f"Test Post" in self.selenium.page_source)

    def test_all_posts_180days(self):
        self.make_a_post()
        self.selenium.get(f"{self.live_server_url}/main/allposts/180days/")
        self.assertTrue(f"Test Post" in self.selenium.page_source)


@override_settings(DEBUG=True)
class IndexPageSystemTest(StaticLiveServerTestCase):
    def setUp(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--disable_gpu")
        self.selenium = WebDriver(chrome_options=self.chrome_options)
        super(IndexPageSystemTest, self).setUp()

        # Set up the test user, post, and messages
        self.create_test_user()
        self.create_test_post()

        # Login.
        self.selenium.get(f"{self.live_server_url}/users/login/")
        field = self.selenium.find_element_by_name("username")
        field.send_keys(USER_NAME)
        field = self.selenium.find_element_by_name("password")
        field.send_keys(PASSWORD)
        field.submit()

        # Go to profile page.
        self.selenium.get(f"{self.live_server_url}/main/")

    def tearDown(self):
        self.selenium.quit()
        super(IndexPageSystemTest, self).tearDown()

    def test_recent_posts(self):
        self.assertTrue(self.test_post.title in self.selenium.page_source,
                        "Test if the test post's title is present on the index page")
        # self.assertTrue("$5.52" in self.selenium.page_source,
        #                 "Test if the test post's price is present on the index page")
        self.assertTrue(format_brief_description(
            "This is a test post with a somewhat long description. " +
            "This description keeps on going.") in self.selenium.page_source,
                        "Test if the test post's description is present on the index page")

    def create_test_user(self):
        """
        Create a user through direct method calls for testing.
        """
        self.test_user = CustomUser.objects.create_user(username=USER_NAME, first_name=FIRST_NAME, last_name=LAST_NAME,
                                                        email=EMAIL, password=PASSWORD)
        # self.test_profile = Profile.objects.create(user=self.test_user, phone_number=PHONE_NUMBER,
        #                                            computing_id=COMPUTING_ID)

    def create_test_post(self):
        self.test_post = Post.objects.create(
            title="Test Post",
            owner=self.test_user,
            description="This is a test post with a somewhat long description. This description keeps on going.",
            pub_date=timezone.now() - datetime.timedelta(days=5),
            price=5.52
        )


@override_settings(DEBUG=True)
class ProfilePageSystemTest(StaticLiveServerTestCase):
    def setUp(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--disable_gpu")
        self.selenium = WebDriver(chrome_options=self.chrome_options)
        super(ProfilePageSystemTest, self).setUp()

        # Set up the test user, post, and messages
        self.create_test_user()
        self.create_test_post()
        self.create_test_message()

        # Login.
        self.selenium.get(f"{self.live_server_url}/users/login/")
        field = self.selenium.find_element_by_name("username")
        field.send_keys(USER_NAME)
        field = self.selenium.find_element_by_name("password")
        field.send_keys(PASSWORD)
        field.submit()

        # Go to profile page.
        self.selenium.get(f"{self.live_server_url}/main/profile/")

    def tearDown(self):
        self.selenium.quit()
        super(ProfilePageSystemTest, self).tearDown()

    def test_name_shown(self):
        self.assertTrue(str(self.test_user) in self.selenium.page_source)

    def test_username_shown(self):
        self.assertTrue(self.test_user.username in self.selenium.page_source)

    def test_email_shown(self):
        self.assertTrue(self.test_user.email in self.selenium.page_source)

    def test_phone_shown(self):
        self.assertTrue("(555) 555-5555" in self.selenium.page_source)

    def test_post_shown(self):
        self.assertTrue(self.test_post.title in self.selenium.page_source,
                        "Test if the test post's title is present on the index page")
        self.assertTrue("$5.52" in self.selenium.page_source,
                        "Test if the test post's price is present on the index page")
        self.assertTrue(format_brief_description(
            "This is a test post with a somewhat long description. " +
            "This description keeps on going.") in self.selenium.page_source,
                        "Test if the test post's description is present on the index page")

    def create_test_user(self):
        """
        Create a user through direct method calls for testing.
        """
        self.test_user = CustomUser.objects.create_user(username=USER_NAME, first_name=FIRST_NAME, last_name=LAST_NAME,
                                                        email=EMAIL, phone_number=PHONE_NUMBER, password=PASSWORD)
        # self.test_profile = Profile.objects.create(user=self.test_user, phone_number=PHONE_NUMBER,
        #                                            computing_id=COMPUTING_ID)

    def create_test_post(self):
        self.test_post = Post.objects.create(title="Test Post", owner=self.test_user,
                                             description="This is a test post with a somewhat long description. " +
                                                         "This description keeps on going.",
                                             pub_date=timezone.now() - datetime.timedelta(days=5), price=5.52)

    def create_test_message(self):
        self.test_message = Message.objects.create(sender=self.test_user, to_post=self.test_post,
                                                   time_sent=timezone.now() - datetime.timedelta(days=4),
                                                   text="This is a test message, sent from myself.", )

