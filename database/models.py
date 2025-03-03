# Do not rename db_table values or field names.
from django.db import models

"""
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
"""

class SolarProjectData(models.Model):
    data_id = models.BigIntegerField(db_column='data_id', blank=True, null=False, primary_key=True)
    locality = models.TextField(db_column='locality', blank=True, null=True)
    region = models.TextField(db_column='region', blank=True, null=True)
    additional_localities = models.TextField(db_column='additional_localities', blank=True, null=True)
    project_name = models.TextField(db_column='project_name', blank=True, null=True)
    project_phase = models.TextField(db_column='project_phase', blank=True, null=True)
    alt_names = models.TextField(db_column='alt_names', blank=True, null=True)
    parent_or_child_project = models.TextField(db_column='parent_or_child_project', blank=True, null=True)
    prev_project_id = models.TextField(db_column='prev_project_id',blank=True,null=True)
    local_action_project_owner = models.TextField(db_column='local_action_project_owner', blank=True, null=True)
    project_mw = models.FloatField(db_column='project_mw', blank=True, null=True)
    phase_mw= models.TextField(db_column='phase_mw', blank=True, null=True)
    local_permit_status = models.TextField(db_column='local_permit_status', blank=True, null=True)
    public_project_acres = models.FloatField(db_column='public_project_acres', blank=True, null=True)
    latitude = models.FloatField(db_column='latitude', blank=True, null=True)
    longitude = models.FloatField(db_column='longitude', blank=True, null=True)
    location_description = models.TextField(db_column='location_description', blank=True, null=True)
    final_action_date = models.TextField(db_column='final_action_date', blank=True, null=True)
    final_action_year = models.TextField(db_column='final_action_year', blank=True, null=True)
    siting_agreement_exists = models.TextField(db_column='siting_agreement_exists', blank=True, null=True)
    siting_agreement_date = models.TextField(db_column='siting_agreement_date', blank=True, null=True)
    siting_agreement_link = models.TextField(db_column='siting_agreement_link', blank=True, null=True)
    deq_permit_number = models.TextField(db_column='deq_permit_number', blank=True, null=True)
    scc_certificate_number = models.TextField(db_column='scc_certificate_number', blank=True, null=True)
    shared_solar_enrolled = models.DateTimeField(db_column='shared_solar_enrolled', blank=True, null=True)
    mined_land = models.TextField(db_column='aml_program_or_funding', blank=True, null=True)
    energy_storage_onsite = models.TextField(db_column='energy_storage_onsite', blank=True, null=True)
    energy_storage_mw = models.TextField(db_column='energy_storage_mw', blank=True, null=True)
    pjm_queue_number = models.TextField(db_column='pjm_queue_number', blank=True, null=True)
    eia_plant_id = models.BigIntegerField(db_column='eia_plant_id', blank=True, null=True)
    eia_operating_status = models.TextField(db_column='eia_operating_status', blank=True, null=True)
    eia_project_status = models.TextField(db_column='eia_project_status', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dev_solar_data_public'

class CountyData(models.Model):
    locality = models.TextField(db_column='locality',primary_key=True)
    fips = models.BigIntegerField(db_column='fips')
    locality_mapping = models.TextField(db_column='locality_mapping')

    class Meta:
        managed = False
        db_table = 'county_fips'

