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
    oeg_page = "Organised_Editing/Activities"
    page_initial_section = "Activities"
    page_template = "==Activities==\n"
    table_template = (
        "===Activities list===\n"
        "{|class='wikitable sortable'\n"
        "|-\n"
        '! scope="col" | Organisation\n'
        '! scope="col" | Platform\n'
        "|-\n"
        "|}\n"
    )
    overview_list_organisation_name_column = 0
    overview_list_platform_name_column = 1


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
    oeg_page = "Organised_Editing/Activities"
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
    projects_list_project_name_column = 0
    projects_list_platform_name_column = 1
    projects_list_project_author_column = 2
    projects_list_project_status_column = 3


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

    users_list_user_id_column = 0
    users_list_user_name_column = 1
