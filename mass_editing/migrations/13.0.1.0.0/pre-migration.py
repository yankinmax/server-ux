 alter table mass_object add column  action_name varchar;

update mass_object set action_name = name;
