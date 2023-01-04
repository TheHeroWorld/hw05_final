from django.test import TestCase
from django.urls import reverse


SLUG = "Slug_test"
USERNAME = "TestUser"
POST_ID = 1


class RoutesTest(TestCase):
    def test_routes(self):
        set_routes = [
            ["index", [], "/"],
            ["group_list", [SLUG], f"/group/{SLUG}/"],
            ["post_create", [], "/create/"],
            ["profile", [USERNAME], f"/profile/{USERNAME}/"],
            ["post_detail", [POST_ID], f"/posts/{POST_ID}/"],
            ["post_edit", [POST_ID], f"/posts/{POST_ID}/edit/"],

        ]
        for route, arg, url in set_routes:
            self.assertEqual(reverse(f"posts:{route}", args=arg), url)
