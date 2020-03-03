#! /usr/bin/python3
import re

from lib.LORISField import LORISField
    
def clean_string(string):
    return re.sub(r'[^\w]', ' ', string).strip()

'''
  Abstract the transformation of a UKBiobank category into a LORIS Instrument (LINST)
'''
class LORISIntrument:
    
    def __init__(self, props = {}, fields = []):
        assert props.get('title', None) is not None, __class__.__name__ + ": title is required"
        assert len(fields) > 0, __class__.__name__ + ": there must be at least one field"
        self.__props = props
        self.__fields = fields
    
    @property
    def description(self):
        return self.__props['descript'] or None
    
    @property
    def instances(self):
        return list(map(lambda f: f.get('instances'),self.__fields))

    
    @property
    def notes(self):
        return self.__props['notes'] or None
    
    @property
    def table_name(self):
        return 'ukbb_' + clean_string(self.title).replace(' ', '_').lower()

    @property
    def title(self):
        return clean_string(self.__props['title'])
    
    def as_LINST(self):
        lines = []
        lines.append('table{@}' + self.table_name + '\n')
        lines.append('title{@}' + self.title + '\n')
        
        if self.description is not None:
            lines.append('static{@}{@}' + self.description + '\n')
            
        if self.notes is not None:
            lines.append('static{@}{@}Notes: ' + self.notes + '\n')
        
        for field in self.__fields:
            f = LORISField(field)
            lines.append(f.as_LINST() + '\n')
        
        return lines
