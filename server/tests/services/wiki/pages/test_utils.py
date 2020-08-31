from unittest.mock import patch

from server.tests.base_test_config import BaseTestCase
from server.services.wiki.pages.utils import generate_document_data_from_wiki_pages
from server.services.wiki.pages.overview_service import OverviewPageService


class TestWikiUtils(BaseTestCase):
    @patch("server.services.wiki.pages.utils." "ProjectPageService.wikitext_to_dict")
    @patch(
        "server.services.wiki.pages.utils." "OrganisationPageService.wikitext_to_dict"
    )
    @patch("server.services.wiki.pages.utils." "OverviewPageService.wikitext_to_dict")
    def test_generate_document_data_from_wiki_pages(
        self, mocked_overview_page, mocked_organisation_page, mocked_project_page
    ):
        mocked_overview_page_dictionary = {
            "Activities": {
                "Activities list": "\n{|class='wikitable sortable'\n"
                "|-\n"
                '! scope="col" | Organisation\n'
                '! scope="col" | Platform\n'
                "|-\n"
                "| [[Organised_Editing/Activities/Organisation name | Organisation name]]\n"
                "| [http://tasks.hotosm.org Organisation name]\n"
                "|-\n"
                "|}"
            }
        }
        mocked_organisation_page_dictionary = {
            "Organisation": {
                "Link": "\n[http://www.example.com Organisation name]\n\n",
                "Description": "\nDescription of organisation\n",
            },
            "Platform": {"Link": "\n[http://tasks.hotosm.org Organisation name]\n\n"},
            "Projects": {
                "Project list": "\n{|class='wikitable sortable'\n"
                "|-\n"
                '! scope="col" | Name\n'
                '! scope="col" | Platform\n'
                '! scope="col" | Project Manager or Team\n'
                '! scope="col" | Status\n'
                "|-\n"
                "| [[Project name | Project name]]\n"
                "| [http://tasks.hotosm.org Organisation name]\n"
                "| wille\n| PUBLISHED\n"
                "|-\n"
                "|}"
            },
        }
        mocked_project_page_dictionary = {
            "Project": {
                "Short Description": "\nHot-project short description\n",
                "Url": "\nhttp://tasks.hotosm.org/projects/1\n",
                "Hashtag": "\n<nowiki>#</nowiki>tm-project-1\n",
                "Timeframe": "\n* '''Start Date:''' 01 April 2019\n",
            },
            "External Sources": {
                "Instructions": "\nInstructions example\n",
                "Per Task Instructions": "\nPer task instructions example\n",
                "Imagery": "\nImagery example\n",
                "License": "\nLicense Example\n",
            },
            "Team and User": {
                "List of Users": '\n{|class="wikitable sortable"\n'
                "|-\n"
                '! scope="col" | OSM ID\n'
                '! scope="col" | Name\n'
                "|-\n"
                "| 1\n"
                "| User\n"
                "|-\n"
                "|}"
            },
        }

        mocked_overview_page.return_value = mocked_overview_page_dictionary
        mocked_organisation_page.return_value = mocked_organisation_page_dictionary
        mocked_project_page.return_value = mocked_project_page_dictionary

        document_data = generate_document_data_from_wiki_pages(
            "Organisation name",
            "Project name",
            {"project": {"name": "update project name"}},
        )
        document_fields = ["organisation", "platform", "project"]
        self.assertCountEqual(list(document_data[0].keys()), document_fields)
        self.assertCountEqual(list(document_data[1].keys()), document_fields)

    @patch("server.services.wiki.pages.utils." "ProjectPageService.wikitext_to_dict")
    @patch(
        "server.services.wiki.pages.utils." "OrganisationPageService.wikitext_to_dict"
    )
    @patch("server.services.wiki.pages.utils." "OverviewPageService.wikitext_to_dict")
    def test_generate_document_data_fails_with_invalid_project(
        self, mocked_overview_page, mocked_organisation_page, mocked_project_page
    ):
        mocked_overview_page_dictionary = {
            "Activities": {
                "Activities list": "\n{|class='wikitable sortable'\n"
                "|-\n"
                '! scope="col" | Organisation\n'
                '! scope="col" | Platform\n'
                "|-\n"
                "| [[Organised_Editing/Activities/Organisation name | Organisation name]]\n"
                "| [http://tasks.hotosm.org Organisation name]\n"
                "|-\n"
                "|}"
            }
        }
        mocked_organisation_page_dictionary = {
            "Organisation": {
                "Link": "\n[http://www.example.com Organisation name]\n\n",
                "Description": "\nDescription of organisation\n",
            },
            "Platform": {"Link": "\n[http://tasks.hotosm.org Organisation name]\n\n"},
            "Projects": {
                "Project list": "\n{|class='wikitable sortable'\n"
                "|-\n"
                '! scope="col" | Name\n'
                '! scope="col" | Platform\n'
                '! scope="col" | Project Manager or Team\n'
                '! scope="col" | Status\n'
                "|-\n"
                "| [[Invalid Project name | Invalid Project name]]\n"
                "| [http://tasks.hotosm.org Organisation name]\n"
                "| wille\n| PUBLISHED\n"
                "|-\n"
                "|}"
            },
        }
        mocked_project_page_dictionary = {
            "Project": {
                "Short Description": "\nHot-project short description\n",
                "Url": "\nhttp://tasks.hotosm.org/projects/1\n",
                "Hashtag": "\n<nowiki>#</nowiki>tm-project-1\n",
                "Timeframe": "\n* '''Start Date:''' 01 April 2019\n",
            },
            "External Sources": {
                "Instructions": "\nInstructions example\n",
                "Per Task Instructions": "\nPer task instructions example\n",
                "Imagery": "\nImagery example\n",
                "License": "\nLicense Example\n",
            },
            "Team and User": {
                "List of Users": '\n{|class="wikitable sortable"\n'
                "|-\n"
                '! scope="col" | OSM ID\n'
                '! scope="col" | Name\n'
                "|-\n"
                "| 1\n"
                "| User\n"
                "|-\n"
                "|}"
            },
        }

        mocked_overview_page.return_value = mocked_overview_page_dictionary
        mocked_organisation_page.return_value = mocked_organisation_page_dictionary
        mocked_project_page.return_value = mocked_project_page_dictionary

        with self.assertRaises(ValueError):
            generate_document_data_from_wiki_pages(
                "Organisation name",
                "Project name",
                {"project": {"name": "update project name"}},
            )

    @patch("server.services.wiki.pages.page_service.MediaWikiService")
    def test_wikitext_to_dict(self, mocked_mediawiki):
        page_text = (
            "==Parent Section==\n===Child section===\nSection text\n"
            "==Second Parent Section==\n===Second Child section===\nSecond section text\n"
        )
        mocked_mediawiki.return_value.get_page_text.return_value = page_text
        mocked_mediawiki.return_value.is_redirect_page.return_value = False
        section_dict = OverviewPageService().wikitext_to_dict("page title")
        expected_section_dict = {
            "Parent Section": {"Child section": "\nSection text\n"},
            "Second Parent Section": {
                "Second Child section": "\nSecond section text\n"
            },
        }
        self.assertDictEqual(section_dict, expected_section_dict)

    @patch("server.services.wiki.pages.page_service.MediaWikiService")
    def test_wikitext_to_dict_fails_with_redirect_page(self, mocked_mediawiki):
        page_text = "#REDIRECT [[redirect page]]"
        mocked_mediawiki.return_value.get_page_text.return_value = page_text
        with self.assertRaises(ValueError):
            OverviewPageService().wikitext_to_dict("page title")

    @patch("server.services.wiki.pages.page_service.MediaWikiService")
    def test_wikitext_to_dict_fails_without_section_with_two_levels(
        self, mocked_mediawiki
    ):
        page_text = "=Section=\npage without section"
        mocked_mediawiki.return_value.get_page_text.return_value = page_text
        mocked_mediawiki.return_value.is_redirect_page.return_value = False
        with self.assertRaises(ValueError):
            OverviewPageService().wikitext_to_dict("page title")
