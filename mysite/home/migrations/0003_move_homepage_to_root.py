from django.db import migrations


def move_homepage_to_root(apps, schema_editor):
    """Delete old /home/ homepage and create new root homepage"""
    # Get models
    ContentType = apps.get_model("contenttypes.ContentType")
    Page = apps.get_model("wagtailcore.Page")
    Site = apps.get_model("wagtailcore.Site")
    HomePage = apps.get_model("home.HomePage")

    # Delete the old homepage at /home/
    HomePage.objects.filter(slug="home", depth=2).delete()

    # Delete the old Site entry
    Site.objects.all().delete()

    # Get the HomePage content type
    homepage_content_type = ContentType.objects.get(model="homepage", app_label="home")

    # Create a new homepage at root level
    # For root pages in Wagtail:
    # - path should be "0001" (depth=1, one position)
    # - slug should be "home" (root pages still have slug)
    # - url_path should be "/"
    homepage = HomePage.objects.create(
        title="Home",
        draft_title="Home",
        slug="home",
        content_type=homepage_content_type,
        path="0001",
        depth=1,
        numchild=0,
        url_path="/",
    )

    # Create a new Site with the homepage as root
    Site.objects.create(hostname="localhost", root_page=homepage, is_default_site=True)


def revert_homepage_to_home(apps, schema_editor):
    """Revert to original /home/ structure"""
    # Get models
    ContentType = apps.get_model("contenttypes.ContentType")
    Page = apps.get_model("wagtailcore.Page")
    Site = apps.get_model("wagtailcore.Site")
    HomePage = apps.get_model("home.HomePage")

    # Delete the root homepage
    HomePage.objects.filter(slug="home", depth=1).delete()

    # Delete the Site
    Site.objects.all().delete()

    # Get the HomePage content type
    homepage_content_type = ContentType.objects.get(model="homepage", app_label="home")

    # Create the original homepage at /home/
    homepage = HomePage.objects.create(
        title="Home",
        draft_title="Home",
        slug="home",
        content_type=homepage_content_type,
        path="00010001",
        depth=2,
        numchild=0,
        url_path="/home/",
    )

    # Create Site
    Site.objects.create(hostname="localhost", root_page=homepage, is_default_site=True)


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0002_create_homepage"),
    ]

    operations = [
        migrations.RunPython(move_homepage_to_root, revert_homepage_to_home),
    ]
