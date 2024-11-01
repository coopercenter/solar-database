# Do not rename db_table values or field names.
from django.db import models


class LocalSolarPolicyData(models.Model):
    id = models.AutoField(primary_key=True)
    locality_name = models.TextField(db_column='Locality Name', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    jurisdiction_type = models.TextField(db_column='Jurisdiction Type', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    jurisdiction_website = models.TextField(db_column='Jurisdiction Website', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    utility_scale_solar_ordinance = models.TextField(db_column='Utility-Scale Solar Ordinance?', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    link_to_ordinance = models.TextField(db_column='Link to Ordinance', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    last_ordinance_update = models.TextField(db_column='Last ordinance update', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    solar_definition = models.TextField(db_column='Solar definition', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    solar_definition_1 = models.TextField(db_column='Solar definition.1', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    solar_principal_use = models.FloatField(db_column='Solar: Principal-Use Largest Definition', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    permitted_zoning_districts = models.TextField(db_column='Permitted Zoning Districts', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    setback_yard_requirements = models.TextField(db_column='Setback/Yard Requirements', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    height = models.TextField(db_column='Height ', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    size_or_density_restrictions = models.TextField(db_column='Size or Density Restrictions (Acreage or MW)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    requires_native_plantings = models.TextField(db_column='Requires native plantings?', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    requires_pollinator_plantings = models.TextField(db_column='Requires pollinator plantings?', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    pollinator_smart_program_reference = models.TextField(db_column='Pollinator-Smart Program Reference', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'local_solar_policy_data'


class SolarProjectMock(models.Model):
    data_id = models.BigIntegerField(db_column='Data ID', blank=True, null=False, primary_key=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    locality = models.TextField(db_column='Locality', blank=True, null=True)  # Field name made lowercase.
    city_county = models.TextField(db_column='City/County', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    project_name = models.TextField(db_column='Project Name', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    alternate_names = models.TextField(db_column='Alternate Names', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    parent_project = models.TextField(db_column='Parent Project', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    data_id_for_previous_project = models.BigIntegerField(db_column='Data ID for Previous Project', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    current_project_owner = models.TextField(db_column='Current Project Owner', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    project_owner = models.TextField(db_column='Project Owner (at local application)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    entity_name = models.TextField(db_column='Entity Name', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    us_eia_entity_name = models.TextField(db_column='US-EIA_Entity Name', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    owner = models.TextField(db_column='Owner', blank=True, null=True)  # Field name made lowercase.
    developer_owner_field = models.TextField(db_column='Developer(s)/Owner(s)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    previous_project_owner_applicant = models.TextField(db_column='Previous project owner/applicant', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    nameplate_capacity_at_local_action = models.BigIntegerField(db_column='Nameplate Capacity at Local Action (MW)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    acreage = models.BigIntegerField(db_column='Acreage', blank=True, null=True)  # Field name made lowercase.
    field_parcel_acreage = models.BigIntegerField(db_column='(Parcel) Acreage', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it started with '_'.
    lease_acreage = models.BigIntegerField(db_column='Lease acreage', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    project_acreage = models.BigIntegerField(db_column='Project Acreage', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    in_fence_area = models.BigIntegerField(db_column='In fence area', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    under_panel_area = models.BigIntegerField(db_column='Under panel area', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    latitude = models.FloatField(db_column='Latitude', blank=True, null=True)  # Field name made lowercase.
    longitude = models.FloatField(db_column='Longitude', blank=True, null=True)  # Field name made lowercase.
    tax_map_parcel = models.BigIntegerField(db_column='Tax Map Parcel # (TMP)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    address = models.TextField(db_column='Address', blank=True, null=True)  # Field name made lowercase.
    land_use_at_time_of_local_application = models.TextField(db_column='Land Use at Time of  Local Application', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    zoning_permit_type = models.TextField(db_column='Zoning Permit Type', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    base_zoning = models.TextField(db_column='Base Zoning', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    zoning = models.TextField(db_column='Zoning', blank=True, null=True)  # Field name made lowercase.
    local_zoning_application_submittal_date = models.TextField(db_column='Local Zoning Application Submittal Date', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    planning_commission_action_date = models.TextField(db_column='Planning Commission action date ', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    additional_planning_commission_dates = models.TextField(db_column='Additional Planning Commission Dates where the project was revi', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    local_bos_and_cc_action_date = models.TextField(db_column='Local (BOS and CC) Action Date', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    additional_bos_cc_dates = models.TextField(db_column='Additional BOS/CC Dates where the project was reviewed', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    local_permit = models.TextField(db_column='Local Permit', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    local_permit_approval = models.TextField(db_column='Local Permit Approval', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    local_permit_status = models.TextField(db_column='Local Permit Status', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    state_permit_path = models.TextField(db_column='State Permit\xa0Path (DEQ or SCC)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    state_permit_source = models.TextField(db_column='State Permit Source', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    vdeq_reps_commercial_operation_commenced = models.TextField(db_column='VDEQ-REPS_Commercial Operation Commenced', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    concurrent_2232 = models.TextField(db_column='Concurrent 2232?', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    status_of_2232_comp_plan_review = models.TextField(db_column='Status of 2232/comp plan review', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    offtaker = models.TextField(db_column='Offtaker', blank=True, null=True)  # Field name made lowercase.
    executed_siting_agreement = models.TextField(db_column='Executed Siting Agreement? ', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    link_to_permit_conditions = models.TextField(db_column='Link to Permit/Conditions, if possible', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    contains_pollinator_smart_features = models.TextField(db_column='Contains Pollinator-Smart Features', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    sheep_grazing = models.TextField(db_column='Sheep Grazing (a type of agrivoltaics)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    agrivoltaic_crop_cover = models.TextField(db_column='Agrivoltaic crop cover', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    apiaries = models.TextField(db_column='Apiaries (beekeeping, a type of agrovoltaics)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    battery_onsite = models.TextField(db_column='Battery Onsite', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    battery_size = models.TextField(db_column='Battery Size', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    axis_design = models.TextField(db_column='Axis Design (Fixed or tilt/tracking)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    panel_type_specified_by_locality = models.TextField(db_column='Panel Type Specified by Locality (CDTE or Crystalline Silicon) ', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    plant_id = models.BigIntegerField(db_column='Plant ID (EIA)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    sector = models.TextField(db_column='Sector (EIA)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    generator_id = models.BigIntegerField(db_column='Generator ID (EIA)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    deq_permit_number = models.BigIntegerField(db_column='DEQ Permit Number', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    # noi_received_date = models.TextField(db_column='NOI Received Date (DEQ, "RENOIREC")', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    interconnection = models.TextField(db_column='Interconnection', blank=True, null=True)  # Field name made lowercase.
    type_of_interconnection = models.TextField(db_column='Type of interconnection', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    operating_month = models.TextField(db_column='Operating Month', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    operating_year = models.TextField(db_column='Operating Year', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    project_status = models.TextField(db_column='Project Status (EIA)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    deq_permit_status = models.TextField(db_column='DEQ Permit Status', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    status_in_the_pjm_queue = models.TextField(db_column='Status in the PJM queue\xa0', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    rps_program_compliance = models.TextField(db_column='RPS Program Compliance', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    rps_development_plan = models.TextField(db_column='RPS Development Plan', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    panel_type = models.TextField(db_column='Panel Type', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    net_metering = models.TextField(db_column='Net-Metering', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    qualifying_facility= models.TextField(db_column='Qualifying Facility (QF)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    qf_ferc_docket_number = models.BigIntegerField(db_column='QF FERC Docket Number', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    operator = models.TextField(db_column='Operator (EIA)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    us_eia_classification = models.TextField(db_column='US-EIA_Classification', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    us_eia_planned_commercial_operation_commence = models.TextField(db_column='US-EIA_Planned Commercial Operation Commence', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    vdeq_reps_construction_commenced = models.TextField(db_column='VDEQ-REPS_Construction Commenced', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    vdeq_edm_permit_mw = models.TextField(db_column='VDEQ-EDM_Permit MW', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    vdeq_emd_permit_name = models.TextField(db_column='VDEQ-EMD_Permit Name', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    entity_id_eia = models.BigIntegerField(db_column='Entity ID (EIA)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    scc_facility_type = models.TextField(db_column='SCC Facility Type', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    scc_cpcn_number = models.BigIntegerField(db_column='SCC CPCN Number', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    vdeq_reps_final_interconnection_agreement_report = models.TextField(db_column='VDEQ-REPS_Final Interconnection Agreement Report', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    pjm_queue = models.TextField(db_column='PJM Queue #', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    deq_swm_status = models.TextField(db_column='DEQ SWM Status', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    total_acreage = models.BigIntegerField(db_column='Total Acreage (DEQ)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.

    class Meta:
        managed = False
        db_table = 'solar_project_data'
    
    def __str__(self):
        return f"{self.project_name}"

class SolarProjectData(models.Model):
    data_id = models.BigIntegerField(db_column='Data ID', blank=True, null=False, primary_key=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    locality = models.TextField(db_column='Locality', blank=True, null=True)  # Field name made lowercase.
    region = models.TextField(db_column='Region', blank=True, null=True)  # Field name made lowercase.
    additional_localities = models.TextField(db_column='Additional Localities', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    project_name = models.TextField(db_column='Project Name', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    project_phases = models.TextField(db_column='Project Phases', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    alternative_names = models.TextField(db_column='Alternative Names', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    owner_developer_at_local_action = models.TextField(db_column='Owner/Developer at Local Action', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    latest_nameplate_capacity_per_local_action_mw_in_ac_field = models.FloatField(db_column='Latest Nameplate Capacity per Local Action (MW in AC)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    phase_mw_in_ac_field = models.TextField(db_column='Phase MW (in AC)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    local_permit_status = models.TextField(db_column='Local Permit Status', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    best_available_project_acreage = models.FloatField(db_column='Best Available Project Acreage', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    latitude = models.FloatField(db_column='Latitude', blank=True, null=True)  # Field name made lowercase.
    longitude = models.FloatField(db_column='Longitude', blank=True, null=True)  # Field name made lowercase.
    location_description = models.TextField(db_column='Location Description', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    date_of_final_action = models.TextField(db_column='Date of Final Action', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    year_of_final_action = models.TextField(db_column='Year of Final Action', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    siting_agreement_executed_field = models.TextField(db_column='Siting Agreement Executed? ', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    date_siting_agreement_executed_field = models.TextField(db_column='Date - Siting Agreement Executed ', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    siting_agreement_link = models.TextField(db_column='Siting Agreement Link', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    deq_permit_number = models.TextField(db_column='DEQ Permit Number', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    scc_certificate_number = models.TextField(db_column='SCC Certificate Number', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    shared_solar_program_enrollled_dominion_field = models.DateTimeField(db_column='Shared Solar Program- Enrollled (Dominion)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    abandoned_mine_land_aml_program_funding_field = models.TextField(db_column='Abandoned Mine Land (AML) program/funding?', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    energy_storage_onsite = models.TextField(db_column='Energy Storage Onsite', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    energy_storage_capacity_mw_field = models.TextField(db_column='Energy Storage Capacity (MW)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    queue_pjm_field = models.TextField(db_column='Queue # (PJM)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    plant_id_eia_field = models.BigIntegerField(db_column='Plant ID (EIA)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    operating_status_eia_field = models.TextField(db_column='Operating Status (EIA)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    project_status_eia_field = models.TextField(db_column='Project Status (EIA)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.

    class Meta:
        managed = False
        db_table = 'solar_data_public'
