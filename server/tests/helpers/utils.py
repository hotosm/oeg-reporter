from datetime import datetime

from server.services.git.file_service import FileService


document_data = {
    "project": {
        "projectId": 1,
        "status": "status example",
        "name": "project name example",
        "shortDescription": "short description example",
        "changesetComment": "changeset comment example",
        "author": "project author example",
        "url": "http://example.com",
        "created": datetime.strftime(
            datetime.strptime("01/01/2020", "%d/%m/%Y"), "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
        "externalSource": {
            "imagery": "imagery example",
            "license": "license example",
            "instructions": "instructions example",
            "perTaskInstructions": "per task instructions example",
        },
        "users": [{"userName": "user name example", "userId": 1}],
    },
    "organisation": {
        "name": "HOT",
        "url": "http://www.hotosm.org/",
        "description": "HOT is an international "
        "team dedicated to humanitarian "
        "action and community development "
        "through open mapping.",
    },
    "platform": {"name": "HOT tasking manager", "url": "http://www.tasks.hotosm.org/"},
}

document_yaml = FileService.dict_to_yaml(document_data)


class OrganisationPageTemplates:
    page_template = (
        "=Activity=\n"
        "==Organisation==\n"
        "===Link===\n"
        "===Description===\n"
        "==Platform==\n"
        "===Link===\n"
    )
    organisation_section = "Organisation"
    platform_section = "Platform"
    organisation_link_section = "Link"
    organisation_description_section = "Description"
    platform_link_section = "Link"
    projects_list_section = "Project list"
    projects_section = "Projects"
    activity_section = "=Activity="
    page_initial_section = "=Activity="
    oeg_page = "Organised_Editing/Activities/Auto_report"
    table_template = (
        "==Projects==\n"
        "===Project list===\n"
        "{|class='wikitable sortable'\n"
        "|-\n"
        '! scope="col" | Name\n'
        '! scope="col" | Platform\n'
        '! scope="col" | Project Manager or Team\n'
        '! scope="col" | Status\n'
        "|-\n"
        "|}\n"
    )
    page_dictionary = {
        "Organisation": {
            "Link": "\n[http://www.hotosm.org/ HOT]\n\n",
            "Description": "HOT is an international "
            "team dedicated to humanitarian "
            "action and community development "
            "through open mapping.",
        },
        "Platform": {"Link": "\n[http://www.tasks.hotosm.org/ HOT tasking manager]\n"},
        "Projects": {
            "Project list": "\n{|class='wikitable sortable'\n|-\n! scope=\"col\" | "
            'Name\n! scope="col" | Platform\n! scope="col" | Project Manager or Team\n! scope="col" | '
            "Status\n|-\n| [[project name example | project name example]]\n|"
            " [http://www.tasks.hotosm.org/ HOT tasking manager]\n| project author example\n| status example\n|-\n|}"
        },
    }


class ProjectPageTemplates:
    page_template = (
        "==Project==\n"
        "===Short Description===\n"
        "===Url===\n"
        "===Hashtag===\n"
        "===Timeframe===\n"
        "===Start Date===\n"
        "==External Sources==\n"
        "===Instructions===\n"
        "===Per Task Instructions===\n"
        "===Imagery===\n"
        "===License===\n"
        "==Metrics==\n"
        "==Quality assurance==\n"
        "==Team and User==\n"
        "===List of Users===\n"
    )
    oeg_page = "Organised_Editing/Activities/Auto_report"
    page_initial_section = "Project"
    project_section = "Project"
    short_description_section = "Short Description"
    timeframe_section = "Timeframe"
    created_date = "Start Date"
    url_section = "Url"
    tools_section = "Tools"
    default_tools_section = "=Default tools"
    external_sources_section = "External Sources"
    per_task_instructions_section = "Per Task Instructions"
    imagery_section = "Imagery"
    license_section = "License"
    standard_changeset_comment_section = "Standard changeset comment"
    hashtag_section = "Hashtag"
    instructions_section = "Instructions"
    metrics_section = "Metrics"
    quality_assurance_section = "Quality assurance"
    team_user_section = "Team and User"
    users_list_section = "List of Users"
    standard_tools = "Standard TM Projects"
    table_template = (
        "==Team and User==\n"
        "===List of Users===\n"
        '{|class="wikitable sortable"\n'
        "|-\n"
        '! scope="col" | OSM ID\n'
        '! scope="col" | Name\n'
        "|-\n"
        "|}\n"
    )
    page_dictionary = {
        "Project": {
            "Short Description": "\nshort description example\n",
            "Url": "\nhttp://example.com/projects/1\n",
            "Hashtag": "\nchangeset comment example\n",
            "Timeframe": "\n* '''Start Date:''' 01 January 2020\n",
        },
        "External Sources": {
            "Instructions": "\ninstructions example\n\n",
            "Per Task Instructions": "\nper task instructions example\n",
            "Imagery": "\nimagery example\n",
            "License": "\nlicense example\n",
        },
        "Team and User": {
            "List of Users": (
                '\n{|class="wikitable sortable"\n|-'
                '\n! scope="col" | OSM ID\n'
                '! scope="col" | Name\n'
                "|-\n"
                "|      1\n|      user name example\n|-\n|}"
            )
        },
    }


class OverviewPageTemplates:
    activities_list_section_title = "Activities list"
    activities_list_table = (
        "{|class='wikitable sortable'\n"
        "|-\n"
        '! scope="col" | Organisation\n'
        '! scope="col" | Platform\n'
        "|-\n"
        "|}\n"
    )
    oeg_page = "Organised_Editing/Activities/Auto_report"
    page_initial_section = "=Activities="
    page_template = "=Activities=\n"
    table_template = (
        "==Activities list==\n"
        "{|class='wikitable sortable'\n"
        "|-\n"
        '! scope="col" | Organisation\n'
        '! scope="col" | Platform\n'
        "|-\n"
        "|}\n"
    )
    page_dictionary = {
        "Activities": {
            "Activities list": (
                "\n{|class='wikitable sortable'\n"
                "|-\n"
                '! scope="col" | Organisation\n'
                '! scope="col" | Platform\n|-\n'
                "| [[Organised_Editing/Activities/HOT | HOT]]\n"
                "| [http://www.tasks.hotosm.org/ HOT tasking manager]\n"
                "|-\n"
                "|}"
            )
        }
    }
