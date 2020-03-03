#! /usr/bin/python3

import os
import csv

from lib.UKBiobankDictionnaries import UKBiobankDictionnaries
    
'''
  This fetch, store and parse the ukbiobank schema files
'''
class UKBiobankSchemas:
    def __init__(self, cachedir=None):
        
        '''
          cache for downlaoded schema files
        '''
        if cachedir is None:
            cachedir = os.path.join(os.getcwd(), '.cache')
            
        if not os.path.exists(cachedir):
            os.mkdir(cachedir, 0o744)
        
        schemadir = os.path.join(cachedir, 'schemas')
        if not os.path.exists(schemadir):
            os.mkdir(schemadir, 0o744)
        
        self.__schemadir = schemadir
        self.__update_schema_doc()
        
        '''
          Internal dictionnaries
        '''        
        self.__subprojects = {}
        self.__load_subprojects()
        
        self.__categories = {}
        self.__load_categories()
        
        self.__encodings = {}
        self.__load_encoding()
        
        self.__fields = {}
        self.__load_fields()
        
        self.__categories_fields_map = {}
        self.__create_category_fields_mapping()
        
    """
        Gets the 999-schema.txt then for each of its rows, get that schema file
    """    
    def __update_schema_doc(self):
        schemafilename = os.path.join(self.__schemadir, '999-schema.txt')
        
        if not os.path.exists(schemafilename):
            self.__getRemoteSchemaDoc(999)
        
        filenames = []
        with open(schemafilename, 'r') as f:
            reader = csv.DictReader(f, delimiter="\t")
            headers = reader.fieldnames
            for row in reader:
                basename = row['schema_id'] + '-' + row['name'] + '.txt'
                filename = os.path.join(self.__schemadir, basename)
                if not os.path.exists(filename):
                    self.__getRemoteSchemaDoc(row['schema_id'])
   
    """
        Loads the UKB encodings from 2-encoding.txt
    """
    def __load_encoding(self):
        filename = os.path.join(self.__schemadir, '2-encoding.txt')
        with open(filename, 'r') as f:
            reader = csv.DictReader(f, delimiter="\t")
            headers = reader.fieldnames
            for row in reader:
                row['values'] = {}
                self.__encodings[row['encoding_id']] = row
        
        valuefiles = ['5-esimpint.txt', '6-esimpstring.txt', '7-esimpreal.txt', '8-esimpdate.txt', '11-ehierint.txt', '12-ehierstring.txt']
        for file in valuefiles:
            filename = os.path.join(self.__schemadir, file)
            with open(filename, 'r', encoding = "ISO-8859-1") as f:
                reader = csv.DictReader(f, delimiter="\t")
                headers = reader.fieldnames
                for row in reader:
                    self.__encodings[row['encoding_id']]['values'][row['value']] = row
                    
    """
        Loads the UKB instances as subprojects (cohorts) from 9-instances.txt
    """
    def __load_subprojects(self):
        filename = os.path.join(self.__schemadir, '9-instances.txt')
        with open(filename, 'r') as f:
            reader = csv.DictReader(f, delimiter="\t")
            headers = reader.fieldnames
            for row in reader:
                self.__subprojects[row['instance_id']] = {
                    "descript": row['descript'],
                    "num_members": row['num_members'],
                    "visits" : {}
                }
                
        self.__load_visits()
        
                
    """
        Loads the UKB cohort visits from 10-insvalue.txt
    """
    def __load_visits(self):
        filename = os.path.join(self.__schemadir, '10-insvalue.txt')
        with open(filename, 'r') as f:
            reader = csv.DictReader(f, delimiter="\t")
            headers = reader.fieldnames
            for row in reader:
                visit = {
                    "descript": row['descript'],
                    "title": row['title']
                }
                self.__subprojects[row['instance_id']]['visits'][row['index']] = visit
     
    """
        Loads the UKB categories from 3-category.txt
    """
    def __load_categories(self):
        filename = os.path.join(self.__schemadir, '3-category.txt')
        with open(filename, 'r') as f:
            reader = csv.DictReader(f, delimiter="\t")
            headers = reader.fieldnames
            for row in reader:
                data = {
                    "availability": row['availability'],
                    "category_id": row['category_id'],
                    "descript": row['descript'],
                    "group_type": row['group_type'],
                    "notes": row['notes'],
                    "title": row['title'],
                    "children": [],
                    "parents": [],
                }
                self.__categories[row['category_id']] = data
                
        self.__populate_child_categories()
    
    """
        Add children ids to the categories using 13-catbrowse.txt
    """
    def __populate_child_categories(self):
        filename = os.path.join(self.__schemadir, '13-catbrowse.txt')
        with open(filename, 'r') as f:
            reader = csv.DictReader(f, delimiter="\t")
            headers = reader.fieldnames
            for row in reader:
                self.__categories[row['parent_id']]['children'].append(row['child_id'])
                self.__categories[row['child_id']]['parents'].append(row['parent_id'])
            
        for category_id in self.__categories:
            if not self.__categories[category_id]['parents'] and category_id != '0':
                self.__categories['0']['children'].append(category_id)
            
            del self.__categories[category_id]['parents']
            
    """
        Add fields using 1-field.txt
    """        
    def __load_fields(self):
        filename = os.path.join(self.__schemadir, '1-field.txt')
        with open(filename, 'r') as f:
            reader = csv.DictReader(f, delimiter="\t")
            headers = reader.fieldnames
            for row in reader:
                self.__fields[row['field_id']] = row
                

    def __create_category_fields_mapping(self):
        for f in self.__fields:  
            cat_id = self.__fields[f]['main_category']
            if not cat_id in self.__categories_fields_map:
                self.__categories_fields_map[cat_id] = []
            self.__categories_fields_map[cat_id].append(f)
            
    
    @property
    def categories_with_fields(self):
        for category_id in self.__categories_fields_map:
            yield {
                "category": self.__categories.get(category_id),
                "fields": list(map(lambda field_id: self.get_field(field_id) ,self.__categories_fields_map.get(category_id)))
            }

    def get_field(self, field_id = ''):
        field = self.__fields.get(field_id)
        if not field:
            raise KeyError('field_id not found')
        
        # Populate a list of expected visits where dataentry occured
        
        subproject = self.__subprojects[field['instance_id']]
        instances = []
        for x in range(int(field['instance_min']), int(field['instance_max'])):
            title = subproject.get('visits', {}).get(str(x), {}).get('title', None)
            instances.append(title)
        
  
        return {
            'field_id': field['field_id'],
            'title': field['title'],
            'notes': field['notes'],
            'debut': field['debut'],
            'version': field['version'],
            'strata': UKBiobankDictionnaries.strata[field['strata']],
            'item_type' : UKBiobankDictionnaries.item_type[field['item_type']],
            'availability': UKBiobankDictionnaries.availability[field['availability']],
            'sexed': UKBiobankDictionnaries.sexed[field['sexed']],
            'encoded': UKBiobankDictionnaries.base_type[field['base_type']],
            'encoding': self.__encodings[field['encoding_id']]['values'],
            'instance_id': field['instance_id'],
            'instances': instances,       
            'item_count': field['item_count'],
            'num_participants': field['num_participants'],
            'value_type': UKBiobankDictionnaries.value_type[field['value_type']],
            'units': field['units'],
            'main_category': self.__categories[field['main_category']]['title'],
        }