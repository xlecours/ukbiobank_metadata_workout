#! /usr/bin/python3
import re

def clean_string(string):
    return re.sub(r'[^\w]', ' ', string).strip()

'''
  Abstract the transformation of a UKBiobank field into a LORIS Instrument row (LINST)
'''

class LORISField:
    def __init__(self, props):
        assert props['field_id'] is not None, __class__.__name__ + "field_id is required"
        assert props['title'] is not None, __class__.__name__ + "title is required"
        self.__props = props

    @property
    def column_name(self):
        return '{}_'.format(self.__props['field_id']) + self.title.replace(' ', '_').lower()[:50]

    @property
    def element_type(self):
        linst_type_mapping = {
            'Compound': 'text',
            'Integer': 'numeric',
            'Categorical (single)': 'select',
            'Categorical (multiple)': 'selectmultiple',
            'Continuous': 'numeric',
            'Text': 'text',
            'Date': 'date',
            'Time': 'numeric'
        }
        
        return linst_type_mapping.get(self.__props.get('value_type', None), 'static')
    
    @property
    def instances(self):
        if self.__props.get('instanced', 0) == 0:
            return []
        
        
        
    @property
    def item_type(self):
        return self.__props.get('item_type', None)
    
    @property
    def label(self):
        return '{} ({})'.format(
            clean_string(self.title),
            self.units
        )
    
    @property
    def options(self):
        options = ''
        if self.__props['value_type'] in ['Categorical (single)', 'Categorical (multiple)']:
            options = 'NULL=>\'\''
            for key in self.__props['encoding'].keys():
                value = self.__props['encoding'][key]['value']
                meaning = self.__props['encoding'][key]['meaning'].replace('\'', '`')
                options += "{-}'" + value + "'=>'" + meaning + "'"
                
        return options
    
    @property
    def strata(self):
        return self.__props.get('strata', None)
    
    @property
    def title(self):
        return clean_string(self.__props['title'])
    
    @property
    def units(self):
        return self.__props.get('units', None)

    def as_LINST(self):
        element_type = self.element_type
        column_name = self.column_name
        label = self.label
        options = self.options
        
        if self.item_type != 'Data': 
            return '{@}'.join(['file', self.column_name, self.label])
        
        if self.strata != 'Primary':
            return '{@}'.join(['static', self.column_name, self.label])
        
        if element_type == 'text':
            return '{@}'.join([element_type, column_name, self.label])
        
        if element_type == 'date':
            options = '{@}{@}'
            
        if element_type == 'numeric':
            options = 'null{@}null'
            
        return '{@}'.join([element_type, column_name, label, options])



            
            
            
            
            
            
            
            
            
            
            
            
            
            