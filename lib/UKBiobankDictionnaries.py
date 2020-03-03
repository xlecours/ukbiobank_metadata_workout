#! /usr/bin/python3

'''
  A dictionnary of value and meaning for fields properties.
'''
class UKBiobankDictionnaries:
    
    availability = {
        '0': True,
        '1': False
    }

    stability = {
        '0': 'Complete',
        '1': 'Updateable',
        '2': 'Accruing',
        '3': 'Ongoing',
    }

    private = {
        '0': False,
        '1': True
    }

    value_type = {
        '101': 'Compound',
        '11': 'Integer',
        '21': 'Categorical (single)',
        '22': 'Categorical (multiple)',
        '31': 'Continuous',
        '41': 'Text',
        '51': 'Date',
        '61': 'Time',
    }

    base_type = {
        '0': 'Not encoded',
        '11': 'Encoded 1', # Encoded
        '41': 'Encoded 2',
    }

    item_type = {
        '0': 'Data',
        '10': 'Samples',
        '20': 'Bulk',
        '30': 'Records',
    }

    strata = {
        '0': 'Primary',
        '1': 'Supporting',
        '2': 'Auxiliary',
        '3': 'Derived',    
    }

    instanced = {
        '0': 'Singular',
        '1': 'Defined',
        '2': 'Variable',
    }

    arrayed = {
        '0': False,
        '1': True
    }

    sexed = {
        '0': 'Both sexes',
        '1': 'Males only',
        '2': 'Females only',  
    }